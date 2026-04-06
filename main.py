# Text-Based RPG Game
import random

# --- GAME CONSTANTS ---
MAP_WIDTH = 15
MAP_HEIGHT = 10
WALL = "█"
FLOOR = "."
PLAYER = "@"
ENEMY = "G"
GOLD = "$"
EXIT = "O"

class Entity:
    """Base class for anything that exists on the grid."""
    def __init__(self, x, y, symbol, name, hp, attack):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack

    def is_alive(self):
        return self.hp > 0

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER, "Hero", hp=30, attack=5)
        self.gold = 0
        self.floor = 1

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

class Enemy(Entity):
    def __init__(self, x, y):
        # Randomize enemy stats slightly
        hp = random.randint(8, 15)
        atk = random.randint(2, 4)
        super().__init__(x, y, ENEMY, "Goblin", hp, atk)

class Dungeon:
    """Manages the 2D grid, movement, and collisions."""
    def __init__(self, player):
        self.grid = []
        self.player = player
        self.enemies = []
        self.items = [] # Stores gold coordinates as tuples: (x, y)
        self.exit_pos = (0, 0)
        self.generate_level()

    def generate_level(self):
        """Creates a new map with walls, enemies, and an exit."""
        self.grid = [[FLOOR for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.enemies.clear()
        self.items.clear()
        
        # Create borders
        for x in range(MAP_WIDTH):
            self.grid[0][x] = WALL
            self.grid[MAP_HEIGHT-1][x] = WALL
        for y in range(MAP_HEIGHT):
            self.grid[y][0] = WALL
            self.grid[y][MAP_WIDTH-1] = WALL
            
        # Add random internal walls
        for _ in range(20):
            wx, wy = random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2)
            self.grid[wy][wx] = WALL

        # Place player
        self.player.x, self.player.y = self.get_empty_space()
        
        # Place enemies (more enemies on higher floors)
        num_enemies = min(3 + self.player.floor, 8)
        for _ in range(num_enemies):
            ex, ey = self.get_empty_space()
            self.enemies.append(Enemy(ex, ey))
            
        # Place gold
        for _ in range(4):
            self.items.append(self.get_empty_space())
            
        # Place Exit
        self.exit_pos = self.get_empty_space()

    def get_empty_space(self):
        """Finds a random tile that isn't a wall or occupied."""
        while True:
            x = random.randint(1, MAP_WIDTH - 2)
            y = random.randint(1, MAP_HEIGHT - 2)
            if self.grid[y][x] == FLOOR:
                # Check it's not occupied by exit, gold, or enemies
                if (x, y) == self.exit_pos or (x, y) in self.items:
                    continue
                occupied = any(e.x == x and e.y == y for e in self.enemies)
                if not occupied:
                    return x, y

    def draw(self):
        """Renders the 2D array to the terminal."""
        print(f"\n--- FLOOR {self.player.floor} ---")
        print(f"HP: {self.player.hp}/{self.player.max_hp} | Gold: {self.player.gold} | ATK: {self.player.attack}")
        print("Controls: W (Up), A (Left), S (Down), D (Right)")
        
        for y in range(MAP_HEIGHT):
            row_str = ""
            for x in range(MAP_WIDTH):
                # Check what to draw at this coordinate
                if self.player.x == x and self.player.y == y:
                    row_str += self.player.symbol
                else:
                    enemy_here = next((e for e in self.enemies if e.x == x and e.y == y), None)
                    if enemy_here:
                        row_str += enemy_here.symbol
                    elif (x, y) == self.exit_pos:
                        row_str += EXIT
                    elif (x, y) in self.items:
                        row_str += GOLD
                    else:
                        row_str += self.grid[y][x]
            print(row_str)

    def move_player(self, dx, dy):
        """Handles player movement and bumping into things."""
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # 1. Check for Walls
        if self.grid[new_y][new_x] == WALL:
            print("\nYou bumped into a wall.")
            return

        # 2. Check for Enemies (Bump to attack)
        enemy_hit = next((e for e in self.enemies if e.x == new_x and e.y == new_y), None)
        if enemy_hit:
            self.combat(enemy_hit)
            return # Don't move into the space if there's an enemy there

        # 3. Move Player
        self.player.x = new_x
        self.player.y = new_y

        # 4. Check for Gold
        if (new_x, new_y) in self.items:
            found = random.randint(5, 15)
            self.player.gold += found
            self.items.remove((new_x, new_y))
            print(f"\nYou picked up {found} gold!")

        # 5. Check for Exit
        if (new_x, new_y) == self.exit_pos:
            print("\nYou found the stairs! Descending deeper...")
            self.player.floor += 1
            # Heal slightly on floor clear
            self.player.heal(10)
            self.generate_level()

    def combat(self, enemy):
        """Simple bump-combat resolution."""
        print(f"\nYou attack the {enemy.name} for {self.player.attack} damage!")
        enemy.hp -= self.player.attack
        
        if not enemy.is_alive():
            print(f"You defeated the {enemy.name}!")
            self.enemies.remove(enemy)
        else:
            # Enemy retaliates
            print(f"The {enemy.name} hits back for {enemy.attack} damage!")
            self.player.hp -= enemy.attack

def main():
    print("=========================================")
    print("        TERMINAL TOMB EXPLORER           ")
    print("=========================================")
    print("Find the 'O' to descend. 'G' are enemies. '$' is gold.")
    
    player = Player(1, 1) # Initial dummy coordinates
    dungeon = Dungeon(player)
    
    while player.is_alive():
        dungeon.draw()
        move = input("\nAction: ").strip().lower()
        
        if move == 'w':
            dungeon.move_player(0, -1)
        elif move == 's':
            dungeon.move_player(0, 1)
        elif move == 'a':
            dungeon.move_player(-1, 0)
        elif move == 'd':
            dungeon.move_player(1, 0)
        elif move == 'q':
            print("Cowardly abandoning the dungeon...")
            break
        else:
            print("Invalid command. Use WASD to move, or Q to quit.")
            
    if not player.is_alive():
        print("\n💀 YOU DIED! 💀")
        print(f"You made it to Floor {player.floor} and collected {player.gold} gold.")

if __name__ == "__main__":
    main()

import random
import time

# --- GAME DATA ---
ITEMS = ["Iron", "Water", "Medicine", "Tech"]

PLANETS = {
    "Earth": {"pos": 0, "base_prices": {"Iron": 10, "Water": 5, "Medicine": 25, "Tech": 50}},
    "Mars": {"pos": 8, "base_prices": {"Iron": 8, "Water": 20, "Medicine": 30, "Tech": 45}},
    "Titan": {"pos": 20, "base_prices": {"Iron": 15, "Water": 2, "Medicine": 40, "Tech": 60}},
    "Nebula Prime": {"pos": 35, "base_prices": {"Iron": 25, "Water": 30, "Medicine": 15, "Tech": 30}}
}

class Ship:
    """Manages the player's spaceship, cargo, and wallet."""
    def __init__(self, name):
        self.name = name
        self.credits = 100
        self.fuel = 50
        self.max_fuel = 50
        self.cargo = {"Iron": 0, "Water": 0, "Medicine": 0, "Tech": 0}
        self.cargo_space = 20
        self.current_planet = "Earth"

    def current_cargo_amount(self):
        return sum(self.cargo.values())

def get_market_prices(planet_name):
    """Generates slightly randomized prices based on the planet's base economy."""
    base = PLANETS[planet_name]["base_prices"]
    current_prices = {}
    for item in ITEMS:
        # Prices fluctuate by +/- 20%
        fluctuation = random.uniform(0.8, 1.2)
        current_prices[item] = int(base[item] * fluctuation)
    return current_prices

def market(ship):
    """Handles buying and selling goods."""
    prices = get_market_prices(ship.current_planet)
    
    while True:
        print(f"\n--- {ship.current_planet} Market ---")
        print(f"Credits: {ship.credits} | Cargo: {ship.current_cargo_amount()}/{ship.cargo_space}")
        print("Available Goods:")
        for i, item in enumerate(ITEMS, 1):
            print(f"{i}. {item} - Buy: {prices[item]}C | Sell: {int(prices[item] * 0.8)}C | You own: {ship.cargo[item]}")
        print("5. Refuel (2 Credits per 1 Fuel)")
        print("6. Leave Market")
        
        choice = input("Select an option: ")
        
        if choice in ['1', '2', '3', '4']:
            item = ITEMS[int(choice) - 1]
            action = input(f"Do you want to (B)uy or (S)ell {item}? ").upper()
            
            if action == 'B':
                qty = input(f"How many {item} to buy? ")
                if qty.isdigit():
                    qty = int(qty)
                    cost = qty * prices[item]
                    if ship.credits >= cost and (ship.current_cargo_amount() + qty) <= ship.cargo_space:
                        ship.credits -= cost
                        ship.cargo[item] += qty
                        print(f"Bought {qty} {item} for {cost} Credits.")
                    else:
                        print("Not enough credits or cargo space!")
                        
            elif action == 'S':
                qty = input(f"How many {item} to sell? ")
                if qty.isdigit():
                    qty = int(qty)
                    if ship.cargo[item] >= qty:
                        revenue = qty * int(prices[item] * 0.8)
                        ship.credits += revenue
                        ship.cargo[item] -= qty
                        print(f"Sold {qty} {item} for {revenue} Credits.")
                    else:
                        print("You don't have that many to sell!")
        
        elif choice == '5':
            missing_fuel = ship.max_fuel - ship.fuel
            if missing_fuel == 0:
                print("Fuel tank is already full.")
            else:
                cost = missing_fuel * 2
                if ship.credits >= cost:
                    ship.credits -= cost
                    ship.fuel = ship.max_fuel
                    print("Refueled to maximum.")
                else:
                    affordable = ship.credits // 2
                    ship.credits -= affordable * 2
                    ship.fuel += affordable
                    print(f"Could only afford {affordable} fuel.")
                    
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

def random_encounter(ship):
    """Triggers events while traveling in deep space."""
    chance = random.random()
    if chance < 0.2:
        print("\n⚠️ WARNING: Space Pirates intercepted your ship!")
        if ship.credits > 20:
            stolen = int(ship.credits * 0.25)
            ship.credits -= stolen
            print(f"They hacked your accounts and stole {stolen} Credits before warping away!")
        else:
            print("They saw you were broke and left you alone out of pity.")
    elif chance > 0.85:
        print("\n✨ You found an abandoned cargo pod drifting in space!")
        found_credits = random.randint(20, 100)
        ship.credits += found_credits
        print(f"Salvaged {found_credits} Credits from the wreckage.")

def travel(ship):
    """Handles movement between planets and fuel consumption."""
    print("\n--- Navigation Chart ---")
    destinations = [p for p in PLANETS.keys() if p != ship.current_planet]
    
    for i, target in enumerate(destinations, 1):
        dist = abs(PLANETS[ship.current_planet]["pos"] - PLANETS[target]["pos"])
        print(f"{i}. {target} (Distance: {dist} | Fuel Cost: {dist})")
    print(f"{len(destinations) + 1}. Cancel")
    
    choice = input("Where do you want to warp? ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(destinations):
        target_planet = destinations[int(choice) - 1]
        dist = abs(PLANETS[ship.current_planet]["pos"] - PLANETS[target_planet]["pos"])
        
        if ship.fuel >= dist:
            print(f"\n🚀 Initiating warp to {target_planet}...")
            time.sleep(1)
            ship.fuel -= dist
            ship.current_planet = target_planet
            print(f"Arrived at {ship.current_planet}. Fuel remaining: {ship.fuel}/{ship.max_fuel}")
            random_encounter(ship)
        else:
            print("❌ Not enough fuel to reach that destination!")
    elif choice == str(len(destinations) + 1):
        return
    else:
        print("Invalid choice.")

def main():
    print("=========================================")
    print("           GALACTIC MERCHANT             ")
    print("=========================================")
    
    name = input("Enter your ship's name: ")
    if not name.strip():
        name = "The Century Falcon"
        
    ship = Ship(name)
    
    while True:
        print(f"\n=========================================")
        print(f" Ship: {ship.name} | Location: {ship.current_planet}")
        print(f" Credits: {ship.credits}C | Fuel: {ship.fuel}/{ship.max_fuel}")
        print(f"=========================================")
        print("1. Visit Local Market")
        print("2. Travel to Another Planet")
        print("3. View Cargo Hold")
        print("4. Retire (Quit Game)")
        
        choice = input("Captain, what are your orders? ")
        
        if choice == '1':
            market(ship)
        elif choice == '2':
            travel(ship)
        elif choice == '3':
            print("\n--- Cargo Hold ---")
            for item, qty in ship.cargo.items():
                if qty > 0:
                    print(f"{item}: {qty}")
            print(f"Total Space Used: {ship.current_cargo_amount()}/{ship.cargo_space}")
        elif choice == '4':
            print(f"\nYou retired with {ship.credits} Credits. Thanks for playing!")
            break
        else:
            print("\n❌ Invalid command.")
            
        # Check for game over (no fuel, no credits, stuck)
        if ship.fuel == 0 and ship.credits < 2 and ship.current_cargo_amount() == 0:
            print("\n💀 GAME OVER: You are stranded in space with no fuel, no goods, and no money.")
            break

if __name__ == "__main__":
    main()


import random
import time

class Settlement:
    """Manages the player's city, resources, and buildings."""
    def __init__(self, name):
        self.name = name
        self.year = 1
        
        # Resources
        self.population = 10
        self.food = 50
        self.wood = 20
        self.gold = 0
        
        # Buildings
        self.huts = 2       # Each hut houses 5 people
        self.farms = 1      # Generates food
        self.lumberjacks = 0 # Generates wood
        self.mines = 0      # Generates gold
        
    def capacity(self):
        return self.huts * 5

    def end_year(self):
        """Calculates resource generation and consumption for the year."""
        print("\n⏳ A year passes...")
        time.sleep(1)
        
        # Production
        food_gained = self.farms * 15
        wood_gained = self.lumberjacks * 10
        gold_gained = self.mines * 5
        
        self.food += food_gained
        self.wood += wood_gained
        self.gold += gold_gained
        
        # Consumption (Each person eats 1 food per year)
        self.food -= self.population
        
        # Population Growth (If there is excess food and housing space)
        growth = 0
        if self.food > self.population * 2 and self.population < self.capacity():
            growth = random.randint(1, 3)
            # Ensure we don't exceed capacity
            growth = min(growth, self.capacity() - self.population)
            self.population += growth
            
        print(f"🌾 Harvested {food_gained} Food. 🌲 Chopped {wood_gained} Wood. 💰 Mined {gold_gained} Gold.")
        
        # Starvation check
        if self.food < 0:
            starved = abs(self.food)
            self.food = 0
            if starved > self.population:
                starved = self.population
            self.population -= starved
            print(f"💀 Famine! {starved} people starved to death.")
        elif growth > 0:
            print(f"👶 Your settlement grew by {growth} people!")

        self.year += 1

def random_event(settlement):
    """Triggers random events that can help or harm the settlement."""
    chance = random.random()
    if chance < 0.20:
        # 20% chance for a bad event
        events = [
            ("A terrible storm destroyed some resources!", "wood", -10),
            ("Thieves raided your gold stash!", "gold", -15),
            ("A localized blight ruined some crops.", "food", -20)
        ]
        event, resource, amount = random.choice(events)
        
        # Apply the negative effect, ensuring we don't drop below 0
        current_val = getattr(settlement, resource)
        loss = min(current_val, abs(amount))
        setattr(settlement, resource, current_val - loss)
        
        print(f"\n⚠️ WARNING: {event} (Lost {loss} {resource.capitalize()})")
        
    elif chance > 0.85:
        # 15% chance for a good event
        events = [
            ("A wandering trader gifted you supplies!", "gold", 20),
            ("A massive herd of deer migrated through!", "food", 30),
            ("Your workers found an abandoned logging camp.", "wood", 25)
        ]
        event, resource, amount = random.choice(events)
        
        current_val = getattr(settlement, resource)
        setattr(settlement, resource, current_val + amount)
        
        print(f"\n✨ BLESSING: {event} (Gained {amount} {resource.capitalize()})")

def build_menu(city):
    """Handles the building construction interface."""
    while True:
        print("\n--- CONSTRUCTION MENU ---")
        print("1. Build Hut (Cost: 10 Wood) - Adds 5 Population Capacity")
        print("2. Build Farm (Cost: 20 Wood) - Generates 15 Food/Year")
        print("3. Build Lumberjack Camp (Cost: 15 Wood, 10 Gold) - Generates 10 Wood/Year")
        print("4. Build Gold Mine (Cost: 30 Wood) - Generates 5 Gold/Year")
        print("5. Return to Main Menu")
        
        choice = input("What will you build? ")
        
        if choice == '1':
            if city.wood >= 10:
                city.wood -= 10
                city.huts += 1
                print("🛖 Hut built!")
            else:
                print("❌ Not enough Wood.")
        elif choice == '2':
            if city.wood >= 20:
                city.wood -= 20
                city.farms += 1
                print("🌾 Farm built!")
            else:
                print("❌ Not enough Wood.")
        elif choice == '3':
            if city.wood >= 15 and city.gold >= 10:
                city.wood -= 15
                city.gold -= 10
                city.lumberjacks += 1
                print("🌲 Lumberjack Camp built!")
            else:
                print("❌ Not enough resources.")
        elif choice == '4':
            if city.wood >= 30:
                city.wood -= 30
                city.mines += 1
                print("⛏️ Gold Mine built!")
            else:
                print("❌ Not enough Wood.")
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

def main():
    print("=========================================")
    print("       TERMINAL KINGDOM BUILDER          ")
    print("=========================================")
    
    name = input("Name your settlement: ")
    if not name.strip():
        name = "New Haven"
        
    city = Settlement(name)
    
    # Main Game Loop
    while city.population > 0:
        print(f"\n=========================================")
        print(f" Year {city.year} | Settlement: {city.name}")
        print(f"=========================================")
        print(f"👥 Population: {city.population}/{city.capacity()}")
        print(f"🌾 Food: {city.food} | 🌲 Wood: {city.wood} | 💰 Gold: {city.gold}")
        print(f"Buildings: {city.huts} Huts, {city.farms} Farms, {city.lumberjacks} Lumberjacks, {city.mines} Mines")
        print("-----------------------------------------")
        print("1. Open Build Menu")
        print("2. Do nothing and advance the year")
        print("3. Abdicate (Quit Game)")
        
        choice = input("My liege, what is your command? ")
        
        if choice == '1':
            build_menu(city)
        elif choice == '2':
            city.end_year()
            random_event(city)
        elif choice == '3':
            print(f"\nYou abandoned {city.name} in Year {city.year}.")
            break
        else:
            print("\n❌ Invalid command.")
            
    if city.population <= 0:
        print(f"\n💀 Everyone in {city.name} has died. Your settlement fell to ruin in Year {city.year}.")

if __name__ == "__main__":
    main()


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
