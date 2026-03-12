# Text-Based RPG Game

import random
import time

class Entity:
    """Base class for all living things in the game."""
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        # Defense mitigates damage, but damage can't be negative
        actual_damage = max(0, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage

class Player(Entity):
    """The main hero controlled by the user."""
    def __init__(self, name):
        super().__init__(name, hp=100, attack=20, defense=5)
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.inventory = {"Health Potion": 3}

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount):
        self.xp += amount
        print(f"You gained {amount} XP!")
        # Level up threshold scales with current level
        if self.xp >= self.level * 50:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 5
        self.defense += 2
        print(f"\n*** LEVEL UP! You are now level {self.level} ***")
        print(f"Stats increased! HP: {self.max_hp}, ATK: {self.attack}, DEF: {self.defense}\n")

class Enemy(Entity):
    """Monsters the player will fight."""
    def __init__(self, name, hp, attack, defense, xp_reward, gold_reward):
        super().__init__(name, hp, attack, defense)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward

def generate_enemy(player_level):
    """Generates a random enemy based on the player's level."""
    enemies = [
        ("Goblin", 30, 10, 2, 15, 5),
        ("Skeleton", 45, 12, 3, 20, 8),
        ("Orc", 60, 15, 5, 30, 12),
        ("Troll", 100, 20, 8, 50, 25),
        ("Dragon", 250, 40, 15, 200, 100)
    ]
    # Restrict enemy pool to player's current progression
    choices = enemies[:min(len(enemies), player_level + 1)]
    chosen = random.choice(choices)
    return Enemy(*chosen)

def battle(player):
    """Handles the turn-based combat loop."""
    enemy = generate_enemy(player.level)
    print(f"\n--- A wild {enemy.name} appears! ---")
    time.sleep(1)

    while player.is_alive() and enemy.is_alive():
        print(f"\n[{player.name}: {player.hp}/{player.max_hp} HP] | [{enemy.name}: {enemy.hp}/{enemy.max_hp} HP]")
        print("1. Attack")
        print("2. Use Health Potion")
        print("3. Run Away")

        choice = input("Choose your action: ")

        if choice == '1':
            # Player attacks with slight randomization
            dmg = enemy.take_damage(player.attack + random.randint(-3, 3))
            print(f"\nYou attack the {enemy.name} for {dmg} damage!")

            if enemy.is_alive():
                # Enemy retaliates
                enemy_dmg = player.take_damage(enemy.attack + random.randint(-2, 2))
                print(f"The {enemy.name} attacks you for {enemy_dmg} damage!")
                
        elif choice == '2':
            if player.inventory.get("Health Potion", 0) > 0:
                player.inventory["Health Potion"] -= 1
                heal_amount = 40
                player.heal(heal_amount)
                print(f"\nYou use a Health Potion and recover {heal_amount} HP.")
                
                # Using an item takes a turn, enemy attacks
                enemy_dmg = player.take_damage(enemy.attack + random.randint(-2, 2))
                print(f"The {enemy.name} attacks you while you heal for {enemy_dmg} damage!")
            else:
                print("\nYou don't have any Health Potions left!")
                continue # Skip enemy turn so player can choose again
                
        elif choice == '3':
            if random.random() > 0.5: # 50% chance to escape
                print("\nYou successfully ran away!")
                return
            else:
                print("\nYou failed to run away!")
                enemy_dmg = player.take_damage(enemy.attack + random.randint(-2, 2))
                print(f"The {enemy.name} strikes your back for {enemy_dmg} damage!")
        else:
            print("\nInvalid choice. Try again.")
            continue
            
        time.sleep(1)

    # Post-battle resolution
    if player.is_alive():
        print(f"\n*** You defeated the {enemy.name}! ***")
        player.gain_xp(enemy.xp_reward)
        player.gold += enemy.gold_reward
        print(f"You found {enemy.gold_reward} gold. Total gold: {player.gold}")
        
        # 30% chance for the enemy to drop a potion
        if random.random() > 0.7:
            player.inventory["Health Potion"] = player.inventory.get("Health Potion", 0) + 1
            print("The enemy dropped a Health Potion!")
    else:
        print("\n*** You have been defeated in battle... ***")

def shop(player):
    """Simple shop to buy items with gold."""
    print("\n--- Welcome to the Merchant's Tent ---")
    while True:
        print(f"Your Gold: {player.gold}")
        print("1. Buy Health Potion (15 Gold)")
        print("2. Leave Shop")
        
        choice = input("What would you like to do? ")
        if choice == '1':
            if player.gold >= 15:
                player.gold -= 15
                player.inventory["Health Potion"] = player.inventory.get("Health Potion", 0) + 1
                print("You bought 1 Health Potion.")
            else:
                print("You don't have enough gold for that!")
        elif choice == '2':
            print("Leaving shop...")
            break
        else:
            print("Invalid choice.")

def main():
    """Main game loop."""
    print("==================================")
    print("     EPIC TEXT ADVENTURE RPG      ")
    print("==================================")
    
    name = input("Enter your hero's name: ")
    if not name.strip():
        name = "Unknown Hero"
        
    player = Player(name)
    
    while player.is_alive():
        print("\n--- MAIN MENU ---")
        print("1. Explore (Fight Enemies)")
        print("2. View Stats & Inventory")
        print("3. Visit Shop")
        print("4. Rest at Inn (Recover HP - Costs 10 Gold)")
        print("5. Quit Game")
        
        choice = input("What will you do? ")
        
        if choice == '1':
            battle(player)
        elif choice == '2':
            print(f"\n--- {player.name}'s Stats ---")
            print(f"Level: {player.level} | XP: {player.xp}/{player.level * 50}")
            print(f"HP: {player.hp}/{player.max_hp}")
            print(f"Attack: {player.attack} | Defense: {player.defense}")
            print(f"Gold: {player.gold}")
            print("Inventory:", player.inventory)
        elif choice == '3':
            shop(player)
        elif choice == '4':
            if player.hp == player.max_hp:
                print("\nYou are already at full health.")
            elif player.gold >= 10:
                player.gold -= 10
                player.heal(player.max_hp)
                print("\nYou rested at the inn and fully recovered your HP.")
            else:
                print("\nYou don't have enough gold to rest.")
        elif choice == '5':
            print("\nThanks for playing! Goodbye.")
            break
        else:
            print("\nInvalid choice. Please pick a number from 1 to 5.")
            
    if not player.is_alive():
        print(f"\nGame Over! You made it to Level {player.level}.")

if __name__ == "__main__":
    main()
