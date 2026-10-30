// Editor-only helpers for building the Sequel Mod's blueprints from scripts. Never cooked into the game.

using UnrealBuildTool;

public class SequelEditor : ModuleRules
{
	public SequelEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });

		PrivateDependencyModuleNames.AddRange(new string[] {
			"UnrealEd", "AssetRegistry", "BlueprintGraph", "Kismet", "KismetCompiler", "UMG", "UMGEditor", "Slate", "SlateCore"
		});
	}
}
