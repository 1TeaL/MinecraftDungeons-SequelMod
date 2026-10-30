#include "SequelEditorLib.h"

#include "AssetRegistryModule.h"
#include "Blueprint/WidgetTree.h"
#include "Engine/World.h"
#include "Misc/PackageName.h"
#include "Components/PanelWidget.h"
#include "EdGraph/EdGraph.h"
#include "EdGraphSchema_K2.h"
#include "EdGraphUtilities.h"
#include "Engine/Blueprint.h"
#include "K2Node_CallArrayFunction.h"
#include "K2Node_CallFunction.h"
#include "K2Node_ComponentBoundEvent.h"
#include "K2Node_CustomEvent.h"
#include "K2Node_MacroInstance.h"
#include "Kismet/KismetArrayLibrary.h"
#include "K2Node_Event.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/CompilerResultsLog.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "WidgetBlueprint.h"

namespace
{
	UEdGraph* FindGraph(UBlueprint* Blueprint, const FString& GraphName, bool bCreate)
	{
		TArray<UEdGraph*> Graphs;
		Blueprint->GetAllGraphs(Graphs);
		for (UEdGraph* Graph : Graphs)
		{
			if (Graph->GetName() == GraphName)
			{
				return Graph;
			}
		}
		if (!bCreate)
		{
			return nullptr;
		}
		UEdGraph* Graph = FBlueprintEditorUtils::CreateNewGraph(Blueprint, FName(*GraphName), UEdGraph::StaticClass(),
			UEdGraphSchema_K2::StaticClass());
		FBlueprintEditorUtils::AddFunctionGraph<UClass>(Blueprint, Graph, /*bIsUserCreated=*/true, nullptr);
		return Graph;
	}

	bool PinType(FString Type, FEdGraphPinType& Out)
	{
		Out = FEdGraphPinType();
		if (Type.RemoveFromStart(TEXT("array:")))
		{
			Out.ContainerType = EPinContainerType::Array;
		}
		if (Type == TEXT("bool")) { Out.PinCategory = UEdGraphSchema_K2::PC_Boolean; return true; }
		if (Type == TEXT("int")) { Out.PinCategory = UEdGraphSchema_K2::PC_Int; return true; }
		if (Type == TEXT("float")) { Out.PinCategory = UEdGraphSchema_K2::PC_Float; return true; }
		if (Type == TEXT("string")) { Out.PinCategory = UEdGraphSchema_K2::PC_String; return true; }
		if (Type == TEXT("name")) { Out.PinCategory = UEdGraphSchema_K2::PC_Name; return true; }
		if (Type == TEXT("text")) { Out.PinCategory = UEdGraphSchema_K2::PC_Text; return true; }
		if (Type.RemoveFromStart(TEXT("enum:")))
		{
			UEnum* Enum = LoadObject<UEnum>(nullptr, *Type);
			Out.PinCategory = UEdGraphSchema_K2::PC_Byte;
			Out.PinSubCategoryObject = Enum;
			return Enum != nullptr;
		}
		if (Type.RemoveFromStart(TEXT("struct:")))
		{
			UScriptStruct* Struct = LoadObject<UScriptStruct>(nullptr, *Type);
			Out.PinCategory = UEdGraphSchema_K2::PC_Struct;
			Out.PinSubCategoryObject = Struct;
			return Struct != nullptr;
		}
		FName Category;
		if (Type.RemoveFromStart(TEXT("class:"))) { Category = UEdGraphSchema_K2::PC_Class; }
		else if (Type.RemoveFromStart(TEXT("object:"))) { Category = UEdGraphSchema_K2::PC_Object; }
		else if (Type.RemoveFromStart(TEXT("softclass:"))) { Category = UEdGraphSchema_K2::PC_SoftClass; }
		else if (Type.RemoveFromStart(TEXT("softobject:"))) { Category = UEdGraphSchema_K2::PC_SoftObject; }
		if (!Category.IsNone())
		{
			UClass* Class = LoadObject<UClass>(nullptr, *Type);
			if (!Class)
			{
				return false;
			}
			Out.PinCategory = Category;
			Out.PinSubCategoryObject = Class;
			return true;
		}
		return false;
	}
}

bool USequelEditorLib::ImportNodes(UBlueprint* Blueprint, const FString& GraphName, const FString& NodesText)
{
	if (!Blueprint)
	{
		return false;
	}
	UEdGraph* Graph = FindGraph(Blueprint, GraphName, true);
	TSet<UEdGraphNode*> Pasted;
	FEdGraphUtilities::ImportNodesFromText(Graph, NodesText, Pasted);
	for (UEdGraphNode* Node : Pasted)
	{
		Node->CreateNewGuid();
	}
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return Pasted.Num() > 0;
}

FString USequelEditorLib::ExportNodes(UBlueprint* Blueprint, const FString& GraphName)
{
	UEdGraph* Graph = Blueprint ? FindGraph(Blueprint, GraphName, false) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	TSet<UObject*> Nodes;
	for (UEdGraphNode* Node : Graph->Nodes)
	{
		Nodes.Add(Node);
	}
	FString Text;
	FEdGraphUtilities::ExportNodesToText(Nodes, Text);
	return Text;
}

bool USequelEditorLib::ClearGraph(UBlueprint* Blueprint, const FString& GraphName)
{
	UEdGraph* Graph = Blueprint ? FindGraph(Blueprint, GraphName, false) : nullptr;
	if (!Graph)
	{
		return false;
	}
	for (UEdGraphNode* Node : TArray<UEdGraphNode*>(Graph->Nodes))
	{
		FBlueprintEditorUtils::RemoveNode(Blueprint, Node, /*bDontRecompile=*/true);
	}
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return true;
}

bool USequelEditorLib::AddVariable(UBlueprint* Blueprint, const FString& Name, const FString& Type)
{
	FEdGraphPinType Pin;
	if (!Blueprint || !PinType(Type, Pin))
	{
		return false;
	}
	return FBlueprintEditorUtils::AddMemberVariable(Blueprint, FName(*Name), Pin);
}

bool USequelEditorLib::SetVariableDefault(UBlueprint* Blueprint, const FString& Name, const FString& Value)
{
	const int32 Index = Blueprint ? FBlueprintEditorUtils::FindNewVariableIndex(Blueprint, FName(*Name)) : INDEX_NONE;
	if (Index == INDEX_NONE)
	{
		return false;
	}
	Blueprint->NewVariables[Index].DefaultValue = Value;
	FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
	return true;
}

UWidget* USequelEditorLib::AddWidget(UWidgetBlueprint* Blueprint, const FString& Parent, UClass* WidgetClass,
	const FString& Name, bool bIsVariable)
{
	if (!Blueprint || !WidgetClass)
	{
		return nullptr;
	}
	UWidgetTree* Tree = Blueprint->WidgetTree;
	UWidget* Widget = Tree->ConstructWidget<UWidget>(WidgetClass, FName(*Name));
	Widget->bIsVariable = bIsVariable;
	if (Parent.IsEmpty())
	{
		Tree->RootWidget = Widget;
	}
	else
	{
		UPanelWidget* Panel = Cast<UPanelWidget>(Tree->FindWidget(FName(*Parent)));
		if (!Panel)
		{
			return nullptr;
		}
		Panel->AddChild(Widget);
	}
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return Widget;
}

namespace
{
	UEdGraphNode* FindNode(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeName)
	{
		UEdGraph* Graph = Blueprint ? FindGraph(Blueprint, GraphName, false) : nullptr;
		if (!Graph)
		{
			return nullptr;
		}
		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (Node->GetName() == NodeName)
			{
				return Node;
			}
		}
		return nullptr;
	}

	UEdGraphPin* FindPin(UEdGraphNode* Node, const FString& PinName)
	{
		if (!Node)
		{
			return nullptr;
		}
		for (UEdGraphPin* Pin : Node->Pins)
		{
			if (Pin->PinName.ToString() == PinName)
			{
				return Pin;
			}
		}
		return nullptr;
	}

	FString Place(UBlueprint* Blueprint, UEdGraph* Graph, UEdGraphNode* Node, int32 X, int32 Y)
	{
		Node->NodePosX = X;
		Node->NodePosY = Y;
		FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
		return Node->GetName();
	}
}

FString USequelEditorLib::AddEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& OwnerClass,
	const FString& EventName, int32 X, int32 Y)
{
	UClass* Owner = LoadObject<UClass>(nullptr, *OwnerClass);
	UEdGraph* Graph = Blueprint && Owner ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	if (UK2Node_Event* Existing = FBlueprintEditorUtils::FindOverrideForFunction(Blueprint, Owner, FName(*EventName)))
	{
		Existing->bCommentBubbleVisible = false;
		Existing->NodeComment.Empty();
		return Place(Blueprint, Graph, Existing, X, Y);
	}
	FGraphNodeCreator<UK2Node_Event> Creator(*Graph);
	UK2Node_Event* Node = Creator.CreateNode();
	Node->EventReference.SetExternalMember(FName(*EventName), Owner);
	Node->bOverrideFunction = true;
	Creator.Finalize();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddCall(UBlueprint* Blueprint, const FString& GraphName, const FString& Class,
	const FString& FunctionName, int32 X, int32 Y)
{
	UClass* Owner = LoadObject<UClass>(nullptr, *Class);
	UFunction* Function = Owner ? Owner->FindFunctionByName(FName(*FunctionName)) : nullptr;
	UEdGraph* Graph = Blueprint && Function ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	FGraphNodeCreator<UK2Node_CallFunction> Creator(*Graph);
	UK2Node_CallFunction* Node = Creator.CreateNode();
	Node->SetFromFunction(Function);
	Creator.Finalize();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddCustomEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& EventName,
	const FString& Params, int32 X, int32 Y)
{
	UEdGraph* Graph = Blueprint ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	FGraphNodeCreator<UK2Node_CustomEvent> Creator(*Graph);
	UK2Node_CustomEvent* Node = Creator.CreateNode();
	Node->CustomFunctionName = FName(*EventName);
	Creator.Finalize();
	TArray<FString> Parts;
	Params.ParseIntoArray(Parts, TEXT(";"));
	for (const FString& Part : Parts)
	{
		FString Name, Type;
		FEdGraphPinType Pin;
		if (!Part.Split(TEXT("="), &Name, &Type) || !PinType(Type, Pin))
		{
			return FString();
		}
		Node->CreateUserDefinedPin(FName(*Name), Pin, EGPD_Output, /*bUseUniqueName=*/false);
	}
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddSelfCall(UBlueprint* Blueprint, const FString& GraphName, const FString& FunctionName,
	int32 X, int32 Y)
{
	UEdGraph* Graph = Blueprint ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	// The skeleton class must know the function (e.g. a custom event added just before) to give the call its pins.
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	FGraphNodeCreator<UK2Node_CallFunction> Creator(*Graph);
	UK2Node_CallFunction* Node = Creator.CreateNode();
	Node->FunctionReference.SetSelfMember(FName(*FunctionName));
	Creator.Finalize();
	return Node->Pins.Num() > 0 ? Place(Blueprint, Graph, Node, X, Y) : FString();
}

FString USequelEditorLib::AddArrayCall(UBlueprint* Blueprint, const FString& GraphName, const FString& FunctionName,
	int32 X, int32 Y)
{
	UFunction* Function = UKismetArrayLibrary::StaticClass()->FindFunctionByName(FName(*FunctionName));
	UEdGraph* Graph = Blueprint && Function ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	FGraphNodeCreator<UK2Node_CallArrayFunction> Creator(*Graph);
	UK2Node_CallArrayFunction* Node = Creator.CreateNode();
	Node->SetFromFunction(Function);
	Creator.Finalize();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddMacro(UBlueprint* Blueprint, const FString& GraphName, const FString& MacroName, int32 X,
	int32 Y)
{
	UBlueprint* Macros = LoadObject<UBlueprint>(nullptr, TEXT("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros"));
	UEdGraph* Macro = nullptr;
	for (UEdGraph* Candidate : Macros ? Macros->MacroGraphs : TArray<UEdGraph*>())
	{
		if (Candidate->GetName() == MacroName)
		{
			Macro = Candidate;
		}
	}
	UEdGraph* Graph = Blueprint && Macro ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	FGraphNodeCreator<UK2Node_MacroInstance> Creator(*Graph);
	UK2Node_MacroInstance* Node = Creator.CreateNode();
	Node->SetMacroGraph(Macro);
	Creator.Finalize();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddBoundEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& Member,
	const FString& DelegateName, int32 X, int32 Y)
{
	if (!Blueprint)
	{
		return FString();
	}
	// The skeleton class must have the member (a widget marked as a variable) for the event to bind to.
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	UObjectProperty* Property = FindField<UObjectProperty>(Blueprint->SkeletonGeneratedClass, FName(*Member));
	UMulticastDelegateProperty* Delegate = Property
		? FindField<UMulticastDelegateProperty>(Property->PropertyClass, FName(*DelegateName)) : nullptr;
	UEdGraph* Graph = Delegate ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	FGraphNodeCreator<UK2Node_ComponentBoundEvent> Creator(*Graph);
	UK2Node_ComponentBoundEvent* Node = Creator.CreateNode();
	Node->InitializeComponentBoundEventParams(Property, Delegate);
	Creator.Finalize();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddNode(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeClass, int32 X,
	int32 Y)
{
	UClass* Class = LoadObject<UClass>(nullptr, *NodeClass);
	UEdGraph* Graph = Blueprint && Class && Class->IsChildOf(UEdGraphNode::StaticClass())
		? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	UEdGraphNode* Node = NewObject<UEdGraphNode>(Graph, Class);
	Graph->AddNode(Node, /*bFromUI=*/false, /*bSelectNewNode=*/false);
	Node->CreateNewGuid();
	Node->PostPlacedNewNode();
	Node->AllocateDefaultPins();
	return Place(Blueprint, Graph, Node, X, Y);
}

FString USequelEditorLib::AddVariableNode(UBlueprint* Blueprint, const FString& GraphName, const FString& Variable,
	bool bSet, int32 X, int32 Y)
{
	return AddMemberNode(Blueprint, GraphName, FString(), Variable, bSet, X, Y);
}

FString USequelEditorLib::AddMemberNode(UBlueprint* Blueprint, const FString& GraphName, const FString& OwnerClass,
	const FString& Variable, bool bSet, int32 X, int32 Y)
{
	UClass* Owner = OwnerClass.IsEmpty() ? nullptr : LoadObject<UClass>(nullptr, *OwnerClass);
	UEdGraph* Graph = Blueprint && (Owner || OwnerClass.IsEmpty()) ? FindGraph(Blueprint, GraphName, true) : nullptr;
	if (!Graph)
	{
		return FString();
	}
	UK2Node_Variable* Node = bSet
		? static_cast<UK2Node_Variable*>(NewObject<UK2Node_VariableSet>(Graph))
		: static_cast<UK2Node_Variable*>(NewObject<UK2Node_VariableGet>(Graph));
	if (Owner)
	{
		Node->VariableReference.SetExternalMember(FName(*Variable), Owner);
	}
	else
	{
		Node->VariableReference.SetSelfMember(FName(*Variable));
	}
	Graph->AddNode(Node, false, false);
	Node->CreateNewGuid();
	Node->PostPlacedNewNode();
	Node->AllocateDefaultPins();
	return Place(Blueprint, Graph, Node, X, Y);
}

bool USequelEditorLib::Link(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeA, const FString& PinA,
	const FString& NodeB, const FString& PinB)
{
	UEdGraphPin* A = FindPin(FindNode(Blueprint, GraphName, NodeA), PinA);
	UEdGraphPin* B = FindPin(FindNode(Blueprint, GraphName, NodeB), PinB);
	if (!A || !B)
	{
		return false;
	}
	const bool bLinked = GetDefault<UEdGraphSchema_K2>()->TryCreateConnection(A, B);
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return bLinked;
}

bool USequelEditorLib::SetPin(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeName,
	const FString& PinName, const FString& Value)
{
	UEdGraphNode* Node = FindNode(Blueprint, GraphName, NodeName);
	UEdGraphPin* Pin = FindPin(Node, PinName);
	if (!Pin)
	{
		return false;
	}
	const UEdGraphSchema_K2* Schema = GetDefault<UEdGraphSchema_K2>();
	if (Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Object || Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Class
		|| Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_SoftObject || Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_SoftClass)
	{
		UObject* Object = LoadObject<UObject>(nullptr, *Value);
		if (!Object)
		{
			return false;
		}
		Schema->TrySetDefaultObject(*Pin, Object);
	}
	else if (Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Text)
	{
		Schema->TrySetDefaultText(*Pin, FText::FromString(Value));
	}
	else
	{
		Schema->TrySetDefaultValue(*Pin, Value);
	}
	Node->PinDefaultValueChanged(Pin);
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return true;
}

bool USequelEditorLib::SetNodeProperty(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeName,
	const FString& Property, const FString& Value)
{
	UEdGraphNode* Node = FindNode(Blueprint, GraphName, NodeName);
	UProperty* Prop = Node ? FindField<UProperty>(Node->GetClass(), FName(*Property)) : nullptr;
	if (!Prop || !Prop->ImportText(*Value, Prop->ContainerPtrToValuePtr<void>(Node), PPF_None, Node))
	{
		return false;
	}
	Node->ReconstructNode();
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return true;
}

FString USequelEditorLib::Pins(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeName)
{
	UEdGraphNode* Node = FindNode(Blueprint, GraphName, NodeName);
	FString Out;
	if (Node)
	{
		for (UEdGraphPin* Pin : Node->Pins)
		{
			const FString Sub = Pin->PinType.PinSubCategoryObject.IsValid() ? Pin->PinType.PinSubCategoryObject->GetName() : FString();
			Out += FString::Printf(TEXT("%s (%s, %s%s%s)\n"), *Pin->PinName.ToString(),
				Pin->Direction == EGPD_Input ? TEXT("in") : TEXT("out"), *Pin->PinType.PinCategory.ToString(),
				Sub.IsEmpty() ? TEXT("") : TEXT(":"), *Sub);
		}
	}
	return Out;
}

bool USequelEditorLib::MakeLevel(const FString& LevelPath, const TArray<UClass*>& ActorClasses)
{
	UPackage* Package = CreatePackage(nullptr, *LevelPath);
	UWorld* World = UWorld::CreateWorld(EWorldType::Inactive, /*bInformEngineOfWorld=*/false,
		FName(*FPackageName::GetShortName(LevelPath)), Package);
	World->SetFlags(RF_Public | RF_Standalone);
	for (UClass* Class : ActorClasses)
	{
		FActorSpawnParameters Params;
		Params.bNoFail = true;
		if (!Class || !World->SpawnActor<AActor>(Class, FTransform::Identity, Params))
		{
			World->DestroyWorld(false);
			return false;
		}
	}
	FAssetRegistryModule::AssetCreated(World);
	Package->MarkPackageDirty();
	const FString File = FPackageName::LongPackageNameToFilename(LevelPath, FPackageName::GetMapPackageExtension());
	const bool bSaved = UPackage::SavePackage(Package, World, RF_Public | RF_Standalone, *File);
	World->DestroyWorld(false);
	return bSaved;
}

FString USequelEditorLib::Compile(UBlueprint* Blueprint)
{
	if (!Blueprint)
	{
		return TEXT("no blueprint");
	}
	FCompilerResultsLog Results;
	FKismetEditorUtilities::CompileBlueprint(Blueprint, EBlueprintCompileOptions::None, &Results);
	FString Out;
	for (const TSharedRef<FTokenizedMessage>& Message : Results.Messages)
	{
		if (Message->GetSeverity() <= EMessageSeverity::Warning)
		{
			Out += Message->ToText().ToString() + TEXT("\n");
		}
	}
	return Out;
}
