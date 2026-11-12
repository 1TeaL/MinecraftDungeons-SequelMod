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
#include "GameFramework/GameStateBase.h"
#include "GameplayEffectUIData.h"
#include "GameplayCueNotify_Static.h"
#include "Blueprint/UserWidget.h"
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

/** The base of everything gear gives its wearer (enchantments are these components on the wearer). */
UCLASS(Blueprintable)
class DUNGEONS_API UGearUtil : public UActorComponent
{
	GENERATED_BODY()
};

/** One enchantment on its wearer, at its level. */
UCLASS(Blueprintable)
class DUNGEONS_API UEnchantment : public UGearUtil
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadOnly)
	int32 Level;

	/** Shows the enchantment's "triggered" icon on the left of its wearer's screen (the game's own, e.g. the
	 *  "x23 Sweeping Edge" Knockback's code shows; a client call in the game). */
	UFUNCTION(BlueprintCallable)
	void BroadcastEnchantmentTriggeredEvent(bool canCombo) const {}
};

/** An enchantment that does its thing every PulseInterval seconds. */
UCLASS(Blueprintable)
class DUNGEONS_API UIntervalExecutionEnchantment : public UEnchantment
{
	GENERATED_BODY()
};

/** Gravity Pulse (armor): pulls nearby mobs in every PulseInterval seconds; the game's own values as defaults, so a
 *  blueprint that sets other values writes them. */
UCLASS(Blueprintable)
class DUNGEONS_API UGravityPulse : public UIntervalExecutionEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float BaseRadius = 400.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float PulseInterval = 3.0f;
};

/** Sponge Strike (melee, unique-only; its only item gets Pain Cycle instead): the host of Shadowcloak
 *  (unreal/Scripts/build_enchants.py). */
UCLASS(Blueprintable)
class DUNGEONS_API USpongeStrike : public UEnchantment
{
	GENERATED_BODY()
};

/** Rushdown (melee, unique-only, no item in the mod carries it): the host of Shadowcloak since 2026-11-08. Its own
 *  speed-up applies Effect on a weapon kill - ours is a do-nothing child, never empty. */
UCLASS(Blueprintable)
class DUNGEONS_API URushdownGameplayEffect : public UGameplayEffect
{
	GENERATED_BODY()
};

UCLASS(Blueprintable)
class DUNGEONS_API URushdown : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<URushdownGameplayEffect> Effect;
};

/** Thrive Under Pressure (armor, unique-only, no item in the mod carries it): the host of Shatter since 2026-11-08.
 *  Defaults differ from ours (0 / 9999) so ours are saved. */
UCLASS(Blueprintable)
class DUNGEONS_API UThriveUnderPressure : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float TriggerRange = 600.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MobThreshold = 4;
};

/** Knockback (melee, unique-only, no item or mob uses it): the host of Sweeping Edge
 *  (unreal/Scripts/build_enchants.py). knockbackPower is the game's own push; ours sets it to 0. The default here is
 *  1 so that a 0 in our blueprint is saved (only values that differ from this parent are saved). */
UCLASS(Blueprintable)
class DUNGEONS_API UKnockback : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float knockbackPower = 1.0f;
};

/** The four unique-only armor enchantments taken over by our own (unreal/Scripts/build_enchants.py): Heals Allies ->
 *  Radiant Guard, Barrier -> Battle Hardened, Shielding -> Last Stand, Regeneration -> Buddy Brew (swapped 2026-11-09). Each one's own
 *  effect is switched off by these settings; the defaults here are the game's, so our changed values are saved. */
UCLASS(Blueprintable)
class DUNGEONS_API UAltruistic : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float PercentageOfDamageToHeal = 0.25f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float AffectionRadius = 1000.0f;
};

UCLASS(Blueprintable)
class DUNGEONS_API UBarrier : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float AffectionRadius = 1500.0f;
};

UCLASS(Blueprintable)
class DUNGEONS_API URegeneration : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float RegenerationAmountPerSecond = 3.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float TimeUntilRegeneration = 10.0f;
};

UCLASS(Blueprintable)
class DUNGEONS_API UShielding : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ShieldMultiplier = 0.95f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ShieldRadius = 1000.0f;
};

/** Damage dealt (all characters; pets get theirs from their artifact). */
UCLASS(Blueprintable)
class DUNGEONS_API UDamageAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float DamageMultiplier;
};

// Refreshment: seconds cut from the potion cooldown per kill (Base at tier I, +PerLevel per tier above).
/** Rampaging (melee): a kill by the weapon has TriggerChance to multiply attack speed by AttackSpeedBoost for
 *  BoostTime x tier s (card: tier x BoostTime, exe+0x32F1B30). Ours (build_enchants.py): chance 0, every kill
 *  credited to the wearer boosts. */
UCLASS(Blueprintable)
class DUNGEONS_API URampaging : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float AttackSpeedBoost = 1.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float BoostTime = 5.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float TriggerChance = 0.1f;
};

/** Electrified (armor): a roll zaps ZapCount mobs within Radius for ZapDamage. Ours (build_enchants.py) keeps it and
 *  adds a share of the zapped mob's max health. Radius / MobZapDamage: the game's defaults aren't known - 0 here, and
 *  never set, so the cooked file leaves them out and the game's own stay. */
UCLASS(Blueprintable)
class DUNGEONS_API UElectrified : public UIntervalExecutionEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ZapDelayMob = 4.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 ZapCountMob = 1;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 ZapCount = 2;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ZapDamage = 50.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float MobZapDamage = 0.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Radius = 0.0f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnBeginRangedAttack);

/** A character's ranged attacks; OnBeginRangedAttack fires at every shot (Accelerating's trigger). Relentless and
 *  Battle Hardened listen to it (a stack per shot). The game's parent is UAttackComponent; only the event matters here. */
UCLASS(Blueprintable)
class DUNGEONS_API URangedAttackComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintAssignable, BlueprintReadWrite, EditAnywhere)
	FOnBeginRangedAttack OnBeginRangedAttack;
};

/** Levitation Shot (ranged; the game's BP_levitationShot is a LevitationRanged): after a roll, the next attack launches
 *  the target. Ours (build_enchants.py) is Relentless; the launch is set to 0. The game's own defaults here; its
 *  "ready" Effect is left out (empty in ours, so none is given). */
/** The "levitation ready" effect Levitation Shot gives on a roll (the game's own class; ours is a do-nothing child). */
UCLASS(Blueprintable)
class DUNGEONS_API ULevitationReadyGameplayEffect : public UGameplayEffect
{
	GENERATED_BODY()
};

UCLASS(Blueprintable)
class DUNGEONS_API ULevitation : public UEnchantment
{
	GENERATED_BODY()

public:
	/** Applied on every roll by the game's code - it must never be empty (an empty one crashed the game on a roll,
	 *  2026-11-08). Ours points it at our do-nothing child. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<ULevitationReadyGameplayEffect> Effect;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Duration = 2.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float EffectStrength = -0.03f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float LaunchStrength = 0.3f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float FallDamagePercentagePerLevel = 0.1f;
};

UCLASS(Blueprintable)
class DUNGEONS_API ULevitationRanged : public ULevitation
{
	GENERATED_BODY()
};

/** Guarding Strike (melee): a kill gives a shield (DamageReduction) for effectBaseDuration + effectDurationPerLevel x
 *  tier s. Ours (build_enchants.py) does it on kill credit; the game's DamageReduction is set to 0. Its effect class is
 *  left out (never set by us, so the game's stays). */
UCLASS(Blueprintable)
class DUNGEONS_API UGuardingStrike : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float effectBaseDuration = 2.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float effectDurationPerLevel = 1.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float DamageReduction = 0.5f;
};

/** Thorns (armor): returns a share of the damage taken. Ours (build_enchants.py) is Overload; the share is set to 0. */
UCLASS(Blueprintable)
class DUNGEONS_API UThorns : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float PercentDamageReturnedBase = 1.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float PercentDamageReturnedPerLevel = 0.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float PercentDamageReturnedMob = 0.1f;
};

/** Thundering (melee): a hit has TriggerChance to strike lightning (StrikeRadius) that chains (IndividualChainRadius).
 *  Ours (build_enchants.py) keeps it and adds a share of the wearer's own hit to the mobs the strike reaches. */
UCLASS(Blueprintable)
class DUNGEONS_API UThundering : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float StrikeRadius = 150.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float IndividualChainRadius = 700.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ChainLightningDelay = 0.1f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float BaseDamage = 12.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float MobDamage = 100.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float TriggerChance = 0.3f;
};

UCLASS(Blueprintable)
class DUNGEONS_API UPotionThirstMelee : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float cooldownReductionBase = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float cooldownReductionPerLevel = 1.0f;
};

UCLASS(Blueprintable)
class DUNGEONS_API UPotionThirstRanged : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float cooldownReductionBase = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float cooldownReductionPerLevel = 1.0f;
};

/** Leeching (melee): a kill by the weapon heals mob max health x (Base + PerLevel x (tier - 1)) (card routine
 *  exe+0x32C8770). Ours (build_enchants.py) sets both 0 and heals on every kill credited to the wearer. */
UCLASS(Blueprintable)
class DUNGEONS_API ULeeching : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float HealPerLevelFactor = 0.02f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float BaseHealFactor = 0.05f;
};

/** Exploding (melee): a kill by the weapon explodes for max health x (Base + PerLevel x (tier - 1)) (card routine
 *  exe+0x32C8440). Ours (build_enchants.py) sets all 0 and explodes every kill credited to the wearer at once. */
UCLASS(Blueprintable)
class DUNGEONS_API UExploding : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float ExplosionRadius = 450.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float explosionMaxHealthFactorBase = 0.2f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float explosionMaxHealthFactorPerLevel = 0.2f;
	/** The look and sound of the game's own (delayed) explosion; ours point both at empty assets of ours. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite) class UParticleSystem* ExplosionEffect = nullptr;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) class USoundCue* ExplosionSound = nullptr;
};

/** Shockwave (melee): the last attack of a combo sends out ShockWaveProjectileClass (BP_ShockwaveProjectile).
 *  Ours (build_enchants.py) keeps all of it and adds a share of the wearer's own hit to the mobs the wave passes.
 *  The game's BP_Shockwave only sets the projectile class; the numbers are SequelMod.toml's. */
UCLASS(Blueprintable)
class DUNGEONS_API UShockwave : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float BaseDamage = 30.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float BaseMoveSpeed = 1850.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float spawnOffset = 150.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float spawnSafetyMargin = 15.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float MobDamage = 125.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<AActor> ShockWaveProjectileClass;
};

/** Swirling (melee): the last attack of a combo spins, damaging mobs within Range. Ours (build_enchants.py) adds a
 *  share of the wearer's own hit to the mobs within Range. */
UCLASS(Blueprintable)
class DUNGEONS_API USwirling : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Range = 400.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float DamageIncreaseFactorPerLevel = 0.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float SwirlBaseDamage = 40.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float MobSwirlDamage = 150.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MinimalHitCountToTrigger = 1;
};

/** Explorer (armor): heals every BlockThreshold blocks explored. The host of Bottomless Brew
 *  (unreal/Scripts/build_enchants.py), whose old heal is switched off with a huge BlockThreshold. */
UCLASS(Blueprintable)
class DUNGEONS_API UExplorer : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 BlockThreshold = 100;
};

/** Recycler (armor): gives arrows every N projectile hits taken. No settings of its own; the host of Ancient Alchemy
 *  (unreal/Scripts/build_enchants.py), whose card text comes from this class's code. */
UCLASS(Blueprintable)
class DUNGEONS_API URecycler : public UEnchantment
{
	GENERATED_BODY()
};

/** Food Reserves' base (it and Surprise Gift make drops when a potion is drunk). */
UCLASS(Blueprintable)
class DUNGEONS_API UStorableDropBaseEnchantment : public UEnchantment
{
	GENERATED_BODY()
};

/** Food Reserves (armor): the host of Barrier Brew (unreal/Scripts/build_enchants.py). Its food count is its per-tier
 *  value, set to 0 in settings/launcher/Formulas.toml, so it crafts nothing. */
UCLASS(Blueprintable)
class DUNGEONS_API UFoodReserves : public UStorableDropBaseEnchantment
{
	GENERATED_BODY()
};

/** Lucky Explorer (armor): emeralds while exploring. The host of Ignite (unreal/Scripts/build_enchants.py); ours sets
 *  PercentageToSpawn 0. The game's default, so the 0 is saved. */
UCLASS(Blueprintable)
class DUNGEONS_API UEmeraldDivination : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float PercentageToSpawn = 0.05f;
	/** Its card's tier number: Base + PerLevel x (tier - 1) (exe+0x32C83E0's routine). Ignite shows 3 / 4 / 5 with it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float EmeraldToSpawnBase = 1.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float EmeraldToSpawnPerLevel = 2.0f;
};

/** Charging Acceleration (ranged, no item has it): the host of Shatter; ours sets AccelerationAmount 0. */
UCLASS(Blueprintable)
class DUNGEONS_API UChargingAcceleration : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float AccelerationAmount = 0.2f;
	/** Its own effect: its code applies it when worn and crashes when it is empty (exe+0xA6B3E9, 2026-11-07) - ours
	 *  links the game's (a placeholder at its path). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<UGameplayEffect> Effect;
};

/** Charging Acceleration's own effect's base (ours: an empty one - the game's showed a "Charged arrows" counter). */
UCLASS(Blueprintable)
class DUNGEONS_API UChargingAccelerationBaseGameplayEffect : public UGameplayEffect
{
	GENERATED_BODY()
};

/** The game's fire and poison enchantments - only named here: our status watcher (build_enchants.py) checks whether a
 *  player wears one (fire / poison damage of a share of the mob's max health). */
UCLASS(Blueprintable)
class DUNGEONS_API UFireAspect : public UEnchantment
{
	GENERATED_BODY()

public:
	// the game's BP_FireAspect sets Effect (its burn); ours (build_enchants.py, 2026-11-12) keeps it - arrows burn too
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<UGameplayEffect> Effect;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float MobDamagePerSecond = 100.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float damagePerSecond = 30.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float fireDuration = 3.0f;
};
/** Shock Web (ranged): beams between the last charged arrows hurt mobs that touch them. Ours (build_enchants.py,
 *  2026-11-12) adds a share of max health and an Overload charge; the game's BP_ShockWeb sets ActorToSpawn (its node
 *  actor) and DeniedProjectiles - ours keeps them. */
UCLASS(Blueprintable)
class DUNGEONS_API UShockWeb : public UEnchantment
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSubclassOf<AActor> ActorToSpawn;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<TSubclassOf<AActor>> DeniedProjectiles;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Range = 2400.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float damagePerSecond = 37.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Period = 0.25f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Duration = 20.0f;
};
UCLASS(Blueprintable)
class DUNGEONS_API UBurning : public UIntervalExecutionEnchantment
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UFireTrail : public UEnchantment
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UPoisoned : public UEnchantment
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UPoisonedMelee : public UPoisoned
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UPoisonedRanged : public UPoisoned
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UJunglePoisonMelee : public UEnchantment
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UJunglePoisonRanged : public UEnchantment
{
	GENERATED_BODY()
};
UCLASS(Blueprintable)
class DUNGEONS_API UDippingPoison : public UEnchantment
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

// OnItemSlotActivationCompletedDelegate.h in the game
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnItemSlotActivationCompleted, UItemSlot*, slot, bool, success);

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

	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool IsOnCooldown() const { return false; }

	/** Broadcast when the slot's item has been used (Artifact Amplifier listens on the artifact slots). */
	UPROPERTY(BlueprintAssignable)
	FOnItemSlotActivationCompleted OnItemSlotActivationCompleted;
};

/** The souls a character carries. */
// OnAnyMobKilledDelegate.h in the game
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAnyMobKilled, AActor*, killedBy);

UCLASS(Blueprintable)
class DUNGEONS_API USoulComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	/** Broadcast when a mob dies, with who killed it (the game's Shadow Feast listens to it). */
	UPROPERTY(BlueprintAssignable)
	FOnAnyMobKilled OnAnyMobKilled;

	/** A server call in the game: adds souls (up to the maximum). */
	UFUNCTION(BlueprintCallable)
	void ServerAddSouls(int32 Amount) {}
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

/** The game's base for its one-shot effects (gameplay cues), e.g. /Game/Cues/HitCues/BP_HitMeleeNotifyStatic - the
 *  spark on every mob a melee swing hits, which our copy replaces to add Sweeping Edge's shockwave. */
UCLASS(Blueprintable)
class DUNGEONS_API UDungeonsGameplayCueNotify_Static : public UGameplayCueNotify_Static
{
	GENERATED_BODY()
};

/** A gameplay effect's buff on the left of the screen (the effect's UIData): its name and icon widget, e.g. the game's
 *  /Game/UI/StatusEffects/GameplayEffect/Icons/UMG_ProtectionIcon. Our timed effects get one (build_enchants.py). */
UCLASS(Blueprintable, EditInlineNew)
class DUNGEONS_API UDungeonsGameplayEffectUIData : public UGameplayEffectUIData
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FText Name;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	TSubclassOf<UUserWidget> iconClass;
};

UCLASS(Blueprintable)
class DUNGEONS_API ADungeonsGameStateBase : public AGameStateBase
{
	GENERATED_BODY()
};

/** The mission's game state. HostileMobsKilled counts every hostile mob killed this mission (all players and pets);
 *  Shadowcloak watches it - the soul component's OnAnyMobKilled only fires for players with soul gathering above 0
 *  (exe+0xA233A0 gates exe+0xA25F90). */
UCLASS(Blueprintable)
class DUNGEONS_API ADungeonsGameState : public ADungeonsGameStateBase
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadOnly)
	int32 HostileMobsKilled = 0;
};

/** The game's audio helpers; CinematicPlaying asks the game state whether a cutscene is playing (exe+0xB83DF0; the
 *  game's own BP_SoundCue uses it). Our overlays hide themselves while it is true. */
UCLASS(Blueprintable)
class DUNGEONS_API UDungeonsAudioUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, BlueprintPure, meta = (WorldContext = "WorldContextObject"))
	static bool CinematicPlaying(UObject* WorldContextObject) { return false; }
};

/** A character's melee numbers (gameplay attributes; Sweeping Edge's effect raises Angle and Range - the game's melee
 *  hit code multiplies each swing's angle and reach by them). */
UCLASS(Blueprintable)
class DUNGEONS_API UMeleeAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackItemPowerFactor;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeHealItemPowerFactor;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackDamageMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackSpeedMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackAngleMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackRangeMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackPushbackMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackLifeStealAmount;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackHitChanceMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float MeleeAttackDamageIncrease;
};

/** A character's ranged numbers (gameplay attributes; Relentless raises damage and speed). The game's own spelling,
 *  "Multipler", kept. */
UCLASS(Blueprintable)
class DUNGEONS_API URangedAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackItemPowerFactor;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedHealItemPowerFactor;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackDamageMultipler;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackSpeedMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackPushbackMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackLifeStealAmount;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackHitChanceMultiplier;
	UPROPERTY(BlueprintReadWrite, EditAnywhere) float RangedAttackDamageIncrease;
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

/** The character's item numbers; Bottomless Brew reads the potion cooldown multiplier (build_enchants.py). */
UCLASS(BlueprintType)
class DUNGEONS_API UItemAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float PotionCooldownMultiplier = 1.0f;

	/** Artifact cooldowns are multiplied by this (the game's cooldown code, exe+0xAEB656); Artificing lowers it. */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ItemCooldownMultiplier = 1.0f;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float ItemDamageMultiplier = 1.0f;

	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	float SoulGatheringMultiplier = 1.0f;
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

/** A character's side. Players and their pets are Heroes; camp animals are not (World...). */
UENUM(BlueprintType)
enum class ETeamName : uint8
{
	Loner,
	Heroes,
	Villains,
	Keys,
	WorldLoner,
	World,
};

UCLASS(Blueprintable)
class DUNGEONS_API ABaseCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	/** Radiant Guard and Buddy Brew help characters on the wearer's team (IsFriendlyTowards also takes animals). */
	UPROPERTY(BlueprintReadWrite, EditAnywhere)
	ETeamName TeamName = ETeamName::Loner;

	/** Same side (players, their pets). Pack Leader finds pets with it. */
	UFUNCTION(BlueprintCallable, BlueprintPure)
	bool IsFriendlyTowards(const ABaseCharacter* Target) const { return false; }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnNormalDamageReceived);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnWeakDamageReceived);

/** A hero (Barrier Brew finds the players near the drinker; Radiant Guard listens to its damage taken). */
UCLASS(Blueprintable)
class DUNGEONS_API APlayerCharacter : public ABaseCharacter
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintAssignable, BlueprintReadWrite, EditAnywhere)
	FOnNormalDamageReceived OnNormalDamageReceived;

	UPROPERTY(BlueprintAssignable, BlueprintReadWrite, EditAnywhere)
	FOnWeakDamageReceived OnWeakDamageReceived;
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
