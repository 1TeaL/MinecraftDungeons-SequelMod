// Stand-ins for the game's own classes, so our blueprints can call them. Names and members are copied from the
// game's class list (UE4SS header dump, Dungeons/Binaries/Win64/ue4ss/UHTHeaderDump). The game finds every call
// and field by name when it loads our blueprints, so only names, parameter order and types have to match - members
// the game keeps private or protected are public here so the blueprint compiler lets us use them. Never shipped:
// the cooked pak holds only our blueprints, and the game has the real classes.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/ChildActorComponent.h"
#include "Engine/GameInstance.h"
#include "AttributeSet.h"
#include "GameplayEffect.h"
#include "GameFramework/Character.h"
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

/** Kinds of actor a dropped item may be on the ground (the drop test counts them). */
UCLASS(Blueprintable)
class DUNGEONS_API AItemActor : public AGearActor
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

UENUM(BlueprintType)
enum class EEquipmentSlot : uint8
{
	HotbarSlot1,
	HotbarSlot2,
	HotbarSlot3,
	MeleeGear,
	RangedGear,
	ArmorGear,
	Invalid,
};

UENUM(BlueprintType)
enum class EItemRarity : uint8
{
	Common,
	Rare,
	Unique,
};

/** One enchantment on an item (our blueprints only pass it along whole; the type/category/source enums are left out). */
USTRUCT(BlueprintType)
struct FEnchantmentData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 Level = 0;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 InvestedPoints = 0;
};

/** One armor property (passed along whole). */
USTRUCT(BlueprintType)
struct FArmorPropertyData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EItemRarity Rarity = EItemRarity::Common;
};

/** One item as the save keeps it. */
USTRUCT(BlueprintType)
struct FInventoryItemData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FSerializableItemId ItemId;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ItemPower = 0.f;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EItemRarity Rarity = EItemRarity::Common;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bHasNetherite = false;

	// The rest, so a blueprint can copy a whole item field by field (Break -> Make) without losing any.
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FEnchantmentData> Enchantments;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FArmorPropertyData> ArmorProperties;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bIsUpgraded = false;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bIsGifted = false;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bIsModified = false;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 timesModified = 0;

	/** The gilded enchantment (with bHasNetherite). */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FEnchantmentData NetheriteEnchantData;
};

/** An item lying on the ground, ready to pick up (the reroll reads what dropped). */
UCLASS(Blueprintable)
class DUNGEONS_API AStorableItem : public AActor
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FInventoryItemData ItemData;

	/** The game's own end of a dropped item's time on the ground (back to its pool). */
	UFUNCTION(BlueprintCallable)
	void TimeToPoolFinished() {}
};

/** An item in the inventory screen. */
UCLASS(Blueprintable)
class DUNGEONS_API UInventoryItem : public UObject
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FInventoryItemData Item;
};

/** A slot of the inventory screen: an inventory cell or an equipment slot. */
UCLASS(Blueprintable)
class DUNGEONS_API UInventoryItemSlot : public UObject
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	ESlotType SlotType;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	UInventoryItem* Item;

	/** What the inventory screen does when an item is dragged onto another slot. */
	UFUNCTION(BlueprintCallable)
	bool Swap(UInventoryItemSlot* Other) { return false; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool CanSwapWith(const UInventoryItemSlot* Other) const { return false; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool IsLocked() const { return false; }
};

/** The player's inventory, storage chest and the list of every item type ever found. */
UCLASS(Blueprintable)
class DUNGEONS_API UItemStashComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool HasPreviouslyFoundItem(const FSerializableItemId& ItemType) const { return false; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	TMap<EEquipmentSlot, UInventoryItemSlot*> GetEquipmentSlots() const { return {}; }

	UFUNCTION(BlueprintCallable, BlueprintPure)
	TArray<UInventoryItemSlot*> GetInventorySlots() const { return {}; }

	UFUNCTION(BlueprintCallable)
	void EnterInventoryUI() {}

	UFUNCTION(BlueprintCallable)
	void ExitInventoryUI() {}
};

/** Mission modifiers (the Daily Trials' "affectors"). */
UENUM(BlueprintType)
enum class EAffectorId : uint8
{
	EmeraldHealthAdd,
	PlayerArrowType,
	PlayerDamage,
	PlayerHealth,
	PlayerSpeed,
	PlayerArtifactCooldown,
	MobDamage,
	MobHealth,
	MobSpeed,
	MobInvisible,
	NightMode,
	PetCount,
	InstantGameOver,
	SoulCount,
	StartupLives,
	ReplaceMeleeMobs,
	ReplaceRangedMobs,
	PlayerEnchantment,
	MobEnchantment,
	ChestProbability,
	PlayerUnderwater,
	MobUnderwater,
	OneShotProtection,
	Last,
};

UENUM(BlueprintType)
enum class EAffectorApplicationType : uint8
{
	None,
	DefaultApplication,
	MidGame,
};

UENUM(BlueprintType)
enum class EAffectorModus : uint8
{
	Easier,
	Harder,
	Any,
};

/** A modifier's setting. Private in the game; which field a modifier reads is not known yet. */
USTRUCT(BlueprintType)
struct FAffectorData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FString Data;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 mInt;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float mFloat;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool mBool;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EAffectorApplicationType ApplicationType;
};

USTRUCT(BlueprintType)
struct FReplicatableModifier
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EAffectorId AffectorId;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FAffectorData AffectorData;
};

USTRUCT(BlueprintType)
struct FReplicatableAffectorsRules
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FReplicatableModifier> Modifiers;
};

/** A modifier as the game's screens show it. */
USTRUCT(BlueprintType)
struct FAffectorInfo
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FText DisplayText;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EAffectorModus Modus;
};

/** Daily Trials: which mission, its modifiers (key -> value text, e.g. mobSpeedMul) and rewards. */
UENUM(BlueprintType)
enum class ELevelNames : uint8 {
	Invalid,
	squidcoast,
	creeperwoods,
	pumpkinpastures,
	soggyswamp,
	mooncorecaverns,
	fieryforge,
	deserttemple,
	slimysewers,
	highblockhalls,
	obsidianpinnacle,
	cacticanyon,
	creeperwoodsdaily,
	creeperwoodsweekly,
	creeperwoodsseasonal,
	pumpkinpasturesdaily,
	pumpkinpasturesweekly,
	pumpkinpasturesseasonal,
	soggyswampdaily,
	soggyswampweekly,
	soggyswampseasonal,
	mooncorecavernsdaily,
	mooncorecavernsweekly,
	mooncorecavernsseasonal,
	fieryforgedaily,
	fieryforgeweekly,
	fieryforgeseasonal,
	deserttempledaily,
	deserttempleweekly,
	deserttempleseasonal,
	slimysewersdaily,
	slimysewersweekly,
	slimysewersseasonal,
	highblockhallsdaily,
	highblockhallsweekly,
	highblockhallsseasonal,
	obsidianpinnacledaily,
	obsidianpinnacleweekly,
	obsidianpinnacleseasonal,
	cacticanyondaily,
	cacticanyonweekly,
	cacticanyonseasonal,
	creepycrypt,
	soggycave,
	underhalls,
	archhaven,
	lowertemple,
	mooshroomisland,
	woodlandmansion,
	spidercave,
	dingyjungle,
	overgrowntemple,
	bamboobluff,
	frozenfjord,
	lonelyfortress,
	lostsettlement,
	creepycryptdaily,
	creepycryptweekly,
	creepycryptseasonal,
	soggycavedaily,
	soggycaveweekly,
	soggycaveseasonal,
	underhallsdaily,
	underhallsweekly,
	underhallsseasonal,
	archhavendaily,
	archhavenweekly,
	archhavenseasonal,
	lowertempledaily,
	lowertempleweekly,
	lowertempleseasonal,
	mooshroomislanddaily,
	mooshroomislandweekly,
	mooshroomislandseasonal,
	dingyjungledaily,
	dingyjungleweekly,
	dingyjungleseasonal,
	overgrowntempledaily,
	overgrowntempleweekly,
	overgrowntempleseasonal,
	bamboobluffdaily,
	bamboobluffweekly,
	bamboobluffseasonal,
	frozenfjorddaily,
	frozenfjordweekly,
	frozenfjordseasonal,
	lonelyfortressdaily,
	lonelyfortressweekly,
	lonelyfortressseasonal,
	lostsettlementdaily,
	lostsettlementweekly,
	lostsettlementseasonal,
	crimsonforest,
	basaltdeltas,
	warpedforest,
	soulsandvalley,
	netherwastes,
	netherfortress,
	netherhypermission,
	crimsonforestdaily,
	crimsonforestweekly,
	crimsonforestseasonal,
	basaltdeltasdaily,
	basaltdeltasweekly,
	basaltdeltasseasonal,
	warpedforestdaily,
	warpedforestweekly,
	warpedforestseasonal,
	soulsandvalleydaily,
	soulsandvalleyweekly,
	soulsandvalleyseasonal,
	netherwastesdaily,
	netherwastesweekly,
	netherwastesseasonal,
	netherfortressdaily,
	netherfortressweekly,
	netherfortressseasonal,
	windsweptpeaks,
	galesanctum,
	endlessrampart,
	gauntletgales,
	windsweptpeaksdaily,
	windsweptpeaksweekly,
	windsweptpeaksseasonal,
	galesanctumdaily,
	galesanctumweekly,
	galesanctumseasonal,
	endlessrampartdaily,
	endlessrampartweekly,
	endlessrampartseasonal,
	gauntletgalesdaily,
	gauntletgalesweekly,
	gauntletgalesseasonal,
	coralrise,
	abyssalmonument,
	radiantravine,
	coralrisedaily,
	coralriseweekly,
	coralriseseasonal,
	abyssalmonumentdaily,
	abyssalmonumentweekly,
	abyssalmonumentseasonal,
	radiantravinedaily,
	radiantravineweekly,
	radiantravineseasonal,
	enderwilds,
	blightedcitadel,
	thestronghold,
	enderwildsdaily,
	enderwildsweekly,
	enderwildsseasonal,
	blightedcitadeldaily,
	blightedcitadelweekly,
	blightedcitadelseasonal,
	thetower,
	freejungle,
	adventurehub,
	randommission,
	specialtileshub,
	hm_hub,
	count,
};

UENUM(BlueprintType)
enum class EExtraChallenge : uint8 {
	Invalid,
	NoExtraChallenge,
	Challenge_1,
	Challenge_2,
	Challenge_3,
	ENUM_COUNT,
};

UENUM(BlueprintType)
enum class EMissionTheme : uint8 {
	Invalid,
	Story,
	Secret,
	Daily,
	Weekly,
	Seasonal,
	Spooky,
	Jungle,
	Winter,
	Mountain,
	Hypermission,
	Anniversary,
	Spooky2021,
	thetower,
	AdventureHub,
	EventWithChallenges,
	EventWithoutChallenges,
	Halloween2022,
	count,
};

USTRUCT(BlueprintType)
struct FPair
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FString Key;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FString Value;
};

USTRUCT(BlueprintType)
struct FReplicatableMap
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FPair> pairs;
};

USTRUCT(BlueprintType)
struct FReplicatableTrialDef
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	ELevelNames Level;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EExtraChallenge ExtraChallenge;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FReplicatableMap Modifiers;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FReplicatableMap> rewards;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FString ID;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FString Type;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EMissionTheme Theme;
};

/** Private in the game. */
USTRUCT(BlueprintType)
struct FReplicatableTrialDefPack
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FReplicatableTrialDef> trialDefs;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool isSet;
};

/** Keeps the trials the game fetched from its server. */
UCLASS(Blueprintable)
class DUNGEONS_API UTrialsProvider : public UObject
{
	GENERATED_BODY()

public:
	/** Protected in the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FReplicatableTrialDefPack CachedTrialDefs;
};

UCLASS(Blueprintable)
class DUNGEONS_API UMinecraftAPI : public UObject
{
	GENERATED_BODY()

public:
	/** Private in the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	UTrialsProvider* TrialsProvider;
};

UCLASS(Blueprintable)
class DUNGEONS_API UDungeonsGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	/** Private in the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	UMinecraftAPI* MinecraftAPI;
};

/** Which A+ level (Apocalypse+ N) a mission is on. */
USTRUCT(BlueprintType)
struct FEndlessStruggle
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 Value;
};

/** A mission's settings (difficulty, A+ level, map...); only passed to ULevelSettingsUtil here, so no members. */
USTRUCT(BlueprintType)
struct FLevelSettings
{
	GENERATED_BODY()
};

UCLASS(Blueprintable)
class DUNGEONS_API ULevelSettingsUtil : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	static FEndlessStruggle getEndlessStruggle(const FLevelSettings& LevelSettings) { return FEndlessStruggle(); }
};

/** A character's health numbers (gameplay attributes; effects change them). */
UCLASS(Blueprintable)
class DUNGEONS_API UHealthAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float Shield;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float Health;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float MaxHealth;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float Barrier;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float MaxBarrier;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float BarrierCharge;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float MaxBarrierCharge;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ResistDeath;

	/** Damage the character takes is multiplied by this. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float TakeDamageMultiplier;
};

/** The game's item dropper: drops new items of a kind - the game rolls their enchantments, power and gilding. */
UCLASS(Blueprintable)
class DUNGEONS_API AItemDropActor : public AInfo
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable)
	void DropItems(const FVector& spawnLocation, const FSerializableItemId& ItemType, const int32 dropCount,
	               AActor* targetPlayer, bool lockItemToOwner) {}
};

/** Which rarity odds a drop uses (exe+0xB51970: common / rare / unique weights) - Mob, WoodenChest and Default
 *  84/15/1, Boss 0/50/50, DeluxeChest and AncientMob 0/75/25, LuxuryMerchant 0/80/20, EventMob 65/25/10. */
UENUM(BlueprintType)
enum class EItemRarityChanceCategory : uint8
{
	Mob,
	Boss,
	WoodenChest,
	FancyChest,
	DeluxeChest,
	LobbyChest,
	MissionEnd,
	PiggyBank,
	ProgressCommand,
	Default,
	EnchantedMobGroup,
	EventMob,
	VillageMerchant,
	LuxuryMerchant,
	PiglinMerchant,
	MysteryBox,
	OnlyCommon,
	AncientMob,
};

UENUM(BlueprintType)
enum class EDropSpawnType : uint8
{
	All,
	Individual,
	Shared,
};

/** The game's base for things that drop items (mobs, chests): the rarity odds they use. */
UCLASS(Blueprintable, ClassGroup = Custom, meta = (BlueprintSpawnableComponent))
class DUNGEONS_API UItemDropComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bEnableDrops;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bElongatedDrops;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ElongatedDropDelay;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ElongatedDropDelayCountSpeedUpFactor;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool bApplyAutomatically;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EItemRarityChanceCategory rarityChanceCategory;

	UFUNCTION(BlueprintCallable)
	void ServerDropItems(const FVector& spawnLocation, AActor* TriggeringPlayer, AActor* Source) {}
};

/** Drops from a list of item kinds; IncludeUniques lets a plain kind come out as one of its uniques. */
UCLASS(Blueprintable, ClassGroup = Custom, meta = (BlueprintSpawnableComponent))
class DUNGEONS_API ULootTableItemDropComponent : public UItemDropComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	EDropSpawnType SpawnType;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FSerializableItemId> LootTable;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float Proability;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 MinCount;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	int32 MaxCount;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	bool IncludeUniques;
};

/** A player's emeralds, gold and Eyes of Ender (on the player character). */
UCLASS(Blueprintable)
class DUNGEONS_API UWalletComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable)
	void Deduct(const FSerializableItemId& Type, int32 Amount) {}

	UFUNCTION(BlueprintCallable, BlueprintPure)
	int32 Balance(const FSerializableItemId& Type) { return 0; }
};

/** The poison of Dipping Poison's arrows (BP_PlayerPoisonArrow applies it on a hit). */
UCLASS(Blueprintable)
class DUNGEONS_API UPoisonArrowGameplayEffect : public UGameplayEffect
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float damagePerSecond = 15.f;
};

/** What the difficulty does to a character. */
UCLASS(Blueprintable)
class DUNGEONS_API UDifficultyAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	/** Damage the character deals is multiplied by this. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float DifficultyDealDamageMultiplier;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float DifficultyPerformHealingMultiplier;
};

/** The big health bar at the top of the screen - only bosses have one. */
UCLASS(Blueprintable)
class DUNGEONS_API UGlobalHealthBarComponent : public UActorComponent
{
	GENERATED_BODY()
};

UCLASS(Blueprintable)
class DUNGEONS_API ABaseCharacter : public ACharacter
{
	GENERATED_BODY()
};

UCLASS(Blueprintable)
class DUNGEONS_API AMobCharacter : public ABaseCharacter
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure)
	FText GetDisplayName() const { return FText(); }
};

/** The mission's game object: level settings and the active modifiers (sent to every player). */
UCLASS(Blueprintable)
class DUNGEONS_API AGameBP : public AInfo
{
	GENERATED_BODY()

public:
	/** Private in the game; the mission's settings (read with ULevelSettingsUtil). */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FLevelSettings mReplicatedLevelSettings_ONLY_FOR_INITIAL_REPLICATION;

	/** Private in the game; the Daily Trials the map shows, sent to the other players, who run OnRep_TrialDefs. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FReplicatableTrialDefPack mTrialDefs;

	/** Private in the game. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	TArray<FAffectorInfo> mActiveAffectorInfo;

	/** Private in the game; sent to the other players, who run OnRep_AffectorsChanged. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	FReplicatableAffectorsRules mReplicatableAffectorsRules;

	UFUNCTION(BlueprintCallable)
	void OnRep_TrialDefs() {}

	UFUNCTION(BlueprintCallable)
	void OnRep_AffectorsChanged() {}

	UFUNCTION(BlueprintCallable, BlueprintPure)
	TArray<FAffectorInfo> GetActiveAffectorInfo() const { return {}; }
};

UCLASS(Blueprintable)
class DUNGEONS_API UActorQuery : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure, meta=(WorldContext="WorldContextObject"))
	static AGameBP* GetGameBP(const UObject* WorldContextObject) { return nullptr; }
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
