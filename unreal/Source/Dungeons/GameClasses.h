// Stand-ins for the game's own classes, so our blueprints can call them. Names and members are copied from the
// game's class list (UE4SS header dump, Dungeons/Binaries/Win64/ue4ss/UHTHeaderDump). The game finds every call
// and field by name when it loads our blueprints, so only names, parameter order and types have to match - members
// the game keeps private or protected are public here so the blueprint compiler lets us use them. Never shipped:
// the cooked pak holds only our blueprints, and the game has the real classes.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/ChildActorComponent.h"
#include "Engine/Texture2D.h"
#include "GameFramework/Info.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GameClasses.generated.h"

UENUM(BlueprintType)
enum class ESlotType : uint8
{
	HealthPotion,
	Arrow,
	BurningArrow,
	FireworksArrow,
	TormentProjectile,
	HeavyHarpoon,
	ThunderingArrow,
	VoidArrow,
	PoisonArrow,
	TNT,
	Trident,
	Conduit,
	ActivePermanent,
	Consumable,
	MeleeWeapon,
	RangedWeapon,
	Armor,
	Any,
	Enchantment,
	None,
	Last,
};

USTRUCT(BlueprintType)
struct FSerializableItemId
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FName SerializedId;
};

/** An empty helper the game places in the menu, camp and mission maps (as /Game/Actors/BP_AvatarInfo); the mod's
 *  copy of that blueprint starts the mod's own actors. */
UCLASS(Blueprintable)
class DUNGEONS_API AAvatarInfo : public AInfo
{
	GENERATED_BODY()
};

/** The look of an item: meshes and materials, attached to the player. */
UCLASS(Blueprintable)
class DUNGEONS_API AGearActor : public AActor
{
	GENERATED_BODY()
};

/** One item in play: its stats and swings. */
UCLASS(Blueprintable)
class DUNGEONS_API AItemInstance : public AInfo
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	FSerializableItemId GetItemId() const { return FSerializableItemId(); }
};

UCLASS(Blueprintable)
class DUNGEONS_API AGearItemInstance : public AItemInstance
{
	GENERATED_BODY()

public:
	/** Which look file to show for this item - the field transmog changes. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TSubclassOf<AGearActor> GearActor;
};

/** One equipment slot on the player (melee, ranged, armor, artifacts). */
UCLASS(Blueprintable)
class DUNGEONS_API UItemSlot : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	ESlotType SlotTypeId;

	UFUNCTION(BlueprintCallable, BlueprintPure)
	AItemInstance* GetItem() const { return nullptr; }
};

UCLASS(Blueprintable)
class DUNGEONS_API UEquipmentComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	TArray<UItemSlot*> GetSlotsOfType(ESlotType Type) const { return {}; }
};

/** Which look (child actor) shows each equipment slot. */
UCLASS(Blueprintable)
class DUNGEONS_API USlotActorManager : public UObject
{
	GENERATED_BODY()

public:
	/** Private in the game. Keyed by slot; rebuilding a slot that isn't here crashes the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TMap<UObject*, UChildActorComponent*> SlotActors;
};

/** Shows the equipped items' looks on a character. */
UCLASS(Blueprintable)
class DUNGEONS_API UEquipmentDisplayComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	/** Private in the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	USlotActorManager* SlotActorManager;

	/** Protected in the game: rebuilds the look of one slot. */
	UFUNCTION(BlueprintCallable)
	void OnGearItemSlotUpdated(UItemSlot* ItemSlot) {}
};

/** The player's inventory, storage chest and the list of every item type ever found. */
UCLASS(Blueprintable)
class DUNGEONS_API UItemStashComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool HasPreviouslyFoundItem(const FSerializableItemId& ItemType) const { return false; }
};

UCLASS(Blueprintable)
class DUNGEONS_API UItemFunctionLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	static FText GetNameForItemType(const FSerializableItemId& Type) { return FText(); }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	static ESlotType GetSlotTypeForItemType(const FSerializableItemId& Type) { return ESlotType::None; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	static FName BreakItemId(const FSerializableItemId& inId) { return NAME_None; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	static UTexture2D* StreamIconTextureForItemIdHigh(const FSerializableItemId& Type, bool blockingLoad) { return nullptr; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	static UTexture2D* GetIconTextureForItemType(const FSerializableItemId& Type) { return nullptr; }
};
