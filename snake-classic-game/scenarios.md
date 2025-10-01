# Scenario 1

Launched simple snake game in pythin

# Scenario 2

Game gets over whenever the snake hits the edge.
Needs to change it. Make it go through edges and 
game gets only over when it hits itself

# Scenario 3

Speed up the snake when the certain score levels are reached

Score 15: 100ms (normal)
Score 16: 95ms  (5% faster)
Score 20: 75ms  (25% faster) 
Score 25: 50ms  (50% faster - maximum speed)

# Scenario 4

Add one bonus food at specific score for extra points

Features:
- Normal food (red): 1 point each - always present
- Bonus food (gold): 5 points - appears only once at score 10
- Bonus food spawns when player reaches exactly 10 points
- After eating bonus food, it's gone forever (one-time reward)
- Food items don't overlap with each other or snake
- Simple, bug-free implementation

# Scenario 5

Enhanced snake visual design

Features:
- Snake head: Bright green circle with white outline and black eyes
- Snake body: Lime green rectangles with green outlines
- Snake tail: Forest green circle (smaller than head)
- Gradient color effect from head to tail
- Enhanced food: Red circles with pink outlines
- Bonus food: Gold circles with orange outline and white star ⭐

# Scenario 6

Dynamic multi-stage progression system with animated backgrounds

Features:
- 5 different stages with unique themes and dynamic backgrounds
- Stage progression every 20 points
- Stage announcement with 2-second display message
- Updated UI showing current stage and theme name
- Animated background effects for each stage

Dynamic Stage Effects:
- Stage 1 (0-19 pts): "Classic Arena" - Twinkling stars that change color
- Stage 2 (20-39 pts): "Ocean Depths" - Moving bubbles and wave patterns
- Stage 3 (40-59 pts): "Crystal Caves" - Purple crystals and sparkle effects
- Stage 4 (60-79 pts): "Jungle Territory" - Leaves and vine patterns
- Stage 5 (80+ pts): "Desert Wasteland" - Sand dunes and particle effects

Animation Features:
- Stars twinkle between white and yellow
- Ocean bubbles float upward and reset
- Crystals and sparkles create mystical atmosphere
- Jungle has organic leaf patterns and vines
- Desert shows realistic dune shapes with sand particles

# Scenario 7

Enhanced scoring system with multipliers and bonuses

Scoring Features:
- Base food: 10 points (instead of 1)
- Bonus food: 50 points (instead of 5)
- Stage multipliers: 1.0x → 1.5x → 2.0x → 2.5x → 3.0x
- Combo system: Eating 3+ foods quickly gives +25 bonus points
- Speed bonus: +5 points when playing at high speed (>50ms)
- Floating point popups show points earned with animations
- Real-time combo counter in the UI

Point Calculation Examples:
- Stage 1 regular food: 10 points
- Stage 3 regular food: 20 points (10 × 2.0x multiplier)
- Stage 5 bonus food: 150 points (50 × 3.0x multiplier)
- Combo bonus: Additional +25 points when active

Simplified Stage Progression:
- Stage advancement: Every 5 foods eaten (not based on score)
- Progress tracker shows "Next: X foods" until next stage
- Much easier to understand and achieve stage progression
- Bonus food appears after eating 10 total foods (not score-based)