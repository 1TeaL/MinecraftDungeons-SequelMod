// What the editor's Python can't do in 4.22: put nodes into a blueprint's graphs, add variables, build a
// widget tree, compile. Called from unreal/Scripts/*.py as unreal.SequelEditorLib.<name>.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SequelEditorLib.generated.h"

class UBlueprint;
class UWidget;
class UWidgetBlueprint;

UCLASS()
class USequelEditorLib : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Paste nodes (the editor's copy/paste text) into a graph: "EventGraph", or a function graph (made if missing). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool ImportNodes(UBlueprint* Blueprint, const FString& GraphName, const FString& NodesText);

	/** The nodes of a graph as copy/paste text - to see how the editor writes a node. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString ExportNodes(UBlueprint* Blueprint, const FString& GraphName);

	/** Remove every node from a graph (to rebuild it from text). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool ClearGraph(UBlueprint* Blueprint, const FString& GraphName);

	/** Add a member variable. Type: bool, int, float, string, name, text, or object:/Script/Module.Class
	 *  (also /Game/... blueprint classes), class:, softclass:, softobject: likewise,
	 *  enum:/Script/Module.EnumName, struct:/Script/Module.StructName; a leading "array:" makes it an array. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool AddVariable(UBlueprint* Blueprint, const FString& Name, const FString& Type);

	/** A variable's default value, as the editor's text (e.g. a soft class path /Game/X/BP_Y.BP_Y_C). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool SetVariableDefault(UBlueprint* Blueprint, const FString& Name, const FString& Value);

	/** Add a widget to a widget blueprint's tree, under Parent (empty: as the root). Returns the widget, whose
	 *  properties Python can then set; IsVariable makes it reachable from the graph. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static UWidget* AddWidget(UWidgetBlueprint* Blueprint, const FString& Parent, UClass* WidgetClass,
		const FString& Name, bool bIsVariable);

	/** An event node: an override of OwnerClass's EventName (e.g. /Script/Engine.Actor, ReceiveBeginPlay), reusing
	 *  the one the blueprint already has. Returns the node's name, which the calls below take. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& OwnerClass,
		const FString& EventName, int32 X, int32 Y);

	/** A call to Class's FunctionName (e.g. /Script/UMG.WidgetBlueprintLibrary, Create). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddCall(UBlueprint* Blueprint, const FString& GraphName, const FString& Class,
		const FString& FunctionName, int32 X, int32 Y);

	/** A custom event - a routine the blueprint calls itself (or a timer calls by name). Params: inputs as
	 *  "Name=type;Name=type" with AddVariable's types. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddCustomEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& EventName,
		const FString& Params, int32 X, int32 Y);

	/** A call to one of the blueprint's own functions or custom events. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddSelfCall(UBlueprint* Blueprint, const FString& GraphName, const FString& FunctionName, int32 X,
		int32 Y);

	/** A call to an array function (Array_Add, Array_Find, Array_Remove...): its item pins take their type from the
	 *  array linked in, so link TargetArray first. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddArrayCall(UBlueprint* Blueprint, const FString& GraphName, const FString& FunctionName, int32 X,
		int32 Y);

	/** A standard macro (ForLoop, ForEachLoop, WhileLoop, Gate, ...). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddMacro(UBlueprint* Blueprint, const FString& GraphName, const FString& MacroName, int32 X, int32 Y);

	/** An event for one of a member's delegates - e.g. a widget blueprint's button Pick (a variable), OnClicked. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddBoundEvent(UBlueprint* Blueprint, const FString& GraphName, const FString& Member,
		const FString& DelegateName, int32 X, int32 Y);

	/** Any other node, by class (e.g. /Script/UMGEditor.K2Node_CreateWidget, /Script/BlueprintGraph.K2Node_IfThenElse). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddNode(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeClass, int32 X, int32 Y);

	/** A get (or set) node for one of the blueprint's own variables. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddVariableNode(UBlueprint* Blueprint, const FString& GraphName, const FString& Variable, bool bSet,
		int32 X, int32 Y);

	/** A get (or set) node for another class's variable (e.g. /Script/Dungeons.GearItemInstance, GearActor); its
	 *  "self" pin takes the object. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString AddMemberNode(UBlueprint* Blueprint, const FString& GraphName, const FString& OwnerClass,
		const FString& Variable, bool bSet, int32 X, int32 Y);

	/** Set one of a node's own settings, as the editor's text, and rebuild its pins - e.g. a cast's TargetType
	 *  (/Script/Dungeons.EquipmentComponent) or an input key node's InputKey (T). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool SetNodeProperty(UBlueprint* Blueprint, const FString& GraphName, const FString& Node,
		const FString& Property, const FString& Value);

	/** Wire NodeA's PinA to NodeB's PinB (an output to an input, or the other way round). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool Link(UBlueprint* Blueprint, const FString& GraphName, const FString& NodeA, const FString& PinA,
		const FString& NodeB, const FString& PinB);

	/** Set an input pin's own value: a literal, or an object/class path for object and class pins. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool SetPin(UBlueprint* Blueprint, const FString& GraphName, const FString& Node, const FString& Pin,
		const FString& Value);

	/** The pins of a node, "name (direction, type)" per line - to see what to wire. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString Pins(UBlueprint* Blueprint, const FString& GraphName, const FString& Node);

	/** Write a level (e.g. /Game/BPLoader/Lobby/SequelHello) holding one actor of each class, at the origin.
	 *  Works headless, unlike EditorLevelLibrary, which needs the editor's own world. */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static bool MakeLevel(const FString& LevelPath, const TArray<UClass*>& ActorClasses);

	/** Compile; returns the compiler's messages (empty when clean). */
	UFUNCTION(BlueprintCallable, Category = "Sequel")
	static FString Compile(UBlueprint* Blueprint);
};
