"""
Help System Component
Displays help menu explaining adaptation strategy and current difficulty adjustment strategy
Requirements: 3.4
"""

from typing import Optional
from game_types import DifficultyLevel, SkillAssessment


class HelpSystem:
    """Manages help menu and adaptation strategy explanations"""

    def __init__(self):
        """Initialize the help system"""
        self.current_difficulty: Optional[DifficultyLevel] = None
        self.current_skill_assessment: Optional[SkillAssessment] = None

    def set_difficulty_level(self, difficulty: DifficultyLevel) -> None:
        """Set the current difficulty level for strategy explanation"""
        self.current_difficulty = difficulty

    def set_skill_assessment(self, assessment: SkillAssessment) -> None:
        """Set the current skill assessment for strategy explanation"""
        self.current_skill_assessment = assessment

    def get_help_menu(self) -> str:
        """Get the main help menu"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║                    SNAKE ADAPTIVE AI - HELP                    ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("GAME CONTROLS:")
        lines.append("  Arrow Keys / WASD - Move snake")
        lines.append("  SPACE - Pause/Resume game")
        lines.append("  P - Open pause menu")
        lines.append("  H - Open help menu")
        lines.append("  Q - Quit game")
        lines.append("")
        lines.append("DIFFICULTY SYSTEM:")
        lines.append("  The game adapts to your skill level automatically.")
        lines.append("  As you improve, the game gets harder.")
        lines.append("  If you struggle, the game becomes easier.")
        lines.append("")
        lines.append("ADAPTIVE PARAMETERS:")
        lines.append("  • Speed: How fast the snake moves (1-10)")
        lines.append("  • Obstacles: Number of obstacles on board (0-5)")
        lines.append("  • Food Spawn Rate: How often food appears (0.5x-2.0x)")
        lines.append("")
        lines.append("SKILL ASSESSMENT:")
        lines.append("  The AI tracks your performance metrics:")
        lines.append("  • Survival Time: How long you last")
        lines.append("  • Food Consumed: How many items you eat")
        lines.append("  • Reaction Time: How quickly you respond")
        lines.append("  • Collisions Avoided: How well you dodge obstacles")
        lines.append("")
        lines.append("DIFFICULTY LEVELS:")
        lines.append("  1-3:   Easy - Good for learning")
        lines.append("  4-6:   Medium - Balanced challenge")
        lines.append("  7-8:   Hard - For experienced players")
        lines.append("  9-10:  Very Hard - Maximum challenge")
        lines.append("")
        lines.append("TIPS:")
        lines.append("  • Play consistently to improve your skill rating")
        lines.append("  • The AI learns from your patterns")
        lines.append("  • Pause to review your performance")
        lines.append("  • Use manual mode for custom difficulty")
        lines.append("")
        lines.append("Press any key to return to game")
        lines.append("")

        return "\n".join(lines)

    def get_adaptation_strategy_explanation(self) -> str:
        """Get explanation of current adaptation strategy in plain language"""
        if not self.current_skill_assessment or not self.current_difficulty:
            return self._get_default_strategy()

        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║              CURRENT ADAPTATION STRATEGY                       ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")

        # Explain current skill level
        skill_level = self.current_skill_assessment.skill_level
        lines.append(f"Your Current Skill Level: {skill_level}/100")
        lines.append("")

        # Explain trend
        trend = self.current_skill_assessment.trend
        if trend == 'improving':
            lines.append("📈 You're improving! The game is getting harder to keep you challenged.")
            lines.append("   • Speed is increasing")
            lines.append("   • More obstacles are being added")
            lines.append("   • Food is becoming scarcer")
        elif trend == 'declining':
            lines.append("📉 You're struggling. The game is getting easier to help you recover.")
            lines.append("   • Speed is decreasing")
            lines.append("   • Fewer obstacles are appearing")
            lines.append("   • More food is available")
        else:
            lines.append("➡️ You're playing consistently. The game is maintaining current difficulty.")
            lines.append("   • Parameters are stable")
            lines.append("   • Challenge level is balanced for your skill")

        lines.append("")

        # Explain current difficulty
        difficulty_level = self.current_difficulty.level
        lines.append(f"Current Difficulty Level: {difficulty_level}/10")
        lines.append("")

        # Explain parameters
        lines.append("Current Parameters:")
        lines.append(f"  • Speed: {self.current_difficulty.speed}/10")
        lines.append(f"  • Obstacles: {self.current_difficulty.obstacle_density}/5")
        lines.append(f"  • Food Spawn Rate: {self.current_difficulty.food_spawn_rate:.1f}x")
        lines.append("")

        # Explain adaptive mode
        if self.current_difficulty.adaptive_mode:
            lines.append("Mode: ADAPTIVE (AI is controlling difficulty)")
        else:
            lines.append("Mode: MANUAL (You are controlling difficulty)")

        lines.append("")
        lines.append("The AI will continue to adjust based on your performance.")
        lines.append("")

        return "\n".join(lines)

    def _get_default_strategy(self) -> str:
        """Get default strategy explanation when no data is available"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║              ADAPTATION STRATEGY                               ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("The AI adaptation system works as follows:")
        lines.append("")
        lines.append("1. MONITORING: The AI tracks your performance metrics")
        lines.append("   • How long you survive")
        lines.append("   • How much food you consume")
        lines.append("   • Your reaction times")
        lines.append("   • How well you avoid obstacles")
        lines.append("")
        lines.append("2. ASSESSMENT: Your skill level is calculated (0-100)")
        lines.append("   • Based on recent performance")
        lines.append("   • Compared to your historical average")
        lines.append("   • Trend is determined (improving/stable/declining)")
        lines.append("")
        lines.append("3. ADJUSTMENT: Difficulty is adjusted automatically")
        lines.append("   • If improving: Game gets harder")
        lines.append("   • If declining: Game gets easier")
        lines.append("   • If stable: Difficulty stays the same")
        lines.append("")
        lines.append("4. SMOOTHING: Changes happen gradually")
        lines.append("   • Transitions occur over 2-3 seconds")
        lines.append("   • No sudden jumps in difficulty")
        lines.append("   • Smooth gameplay experience")
        lines.append("")
        lines.append("Play a game to see the adaptation in action!")
        lines.append("")

        return "\n".join(lines)

    def get_quick_tips(self) -> str:
        """Get quick tips for playing"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║                    QUICK TIPS                                  ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("BEGINNER TIPS:")
        lines.append("  • Start with easy difficulty to learn the controls")
        lines.append("  • Focus on smooth, deliberate movements")
        lines.append("  • Plan your path to food in advance")
        lines.append("")
        lines.append("INTERMEDIATE TIPS:")
        lines.append("  • Watch for patterns in obstacle placement")
        lines.append("  • Use the edges of the board strategically")
        lines.append("  • Maintain consistent reaction times")
        lines.append("")
        lines.append("ADVANCED TIPS:")
        lines.append("  • Predict food spawn locations")
        lines.append("  • Create efficient paths through obstacles")
        lines.append("  • Manage your snake length strategically")
        lines.append("")
        lines.append("GENERAL TIPS:")
        lines.append("  • Pause to review your performance")
        lines.append("  • Check your skill assessment regularly")
        lines.append("  • Play consistently to improve")
        lines.append("  • Use manual mode to practice specific skills")
        lines.append("")

        return "\n".join(lines)

    def get_difficulty_guide(self) -> str:
        """Get guide to difficulty levels"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║                  DIFFICULTY GUIDE                              ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("LEVEL 1-3: EASY")
        lines.append("  Speed: 1-3/10 (Slow)")
        lines.append("  Obstacles: 0-1 (Few)")
        lines.append("  Food: Abundant")
        lines.append("  Best for: Learning, relaxing, practicing")
        lines.append("")
        lines.append("LEVEL 4-6: MEDIUM")
        lines.append("  Speed: 4-6/10 (Moderate)")
        lines.append("  Obstacles: 2-3 (Some)")
        lines.append("  Food: Normal")
        lines.append("  Best for: Balanced gameplay, skill development")
        lines.append("")
        lines.append("LEVEL 7-8: HARD")
        lines.append("  Speed: 7-8/10 (Fast)")
        lines.append("  Obstacles: 4 (Many)")
        lines.append("  Food: Scarce")
        lines.append("  Best for: Experienced players, high scores")
        lines.append("")
        lines.append("LEVEL 9-10: VERY HARD")
        lines.append("  Speed: 9-10/10 (Very Fast)")
        lines.append("  Obstacles: 5 (Maximum)")
        lines.append("  Food: Very Scarce")
        lines.append("  Best for: Experts, maximum challenge")
        lines.append("")

        return "\n".join(lines)

    def get_faq(self) -> str:
        """Get frequently asked questions"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║                  FREQUENTLY ASKED QUESTIONS                    ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("Q: Why did the difficulty suddenly increase?")
        lines.append("A: The AI detected that you're playing well and increased the")
        lines.append("   challenge to keep you engaged. You can switch to manual mode")
        lines.append("   to control difficulty yourself.")
        lines.append("")
        lines.append("Q: How does the AI know my skill level?")
        lines.append("A: The AI analyzes your performance metrics including survival")
        lines.append("   time, food consumption, reaction time, and collision avoidance.")
        lines.append("")
        lines.append("Q: Can I turn off adaptive difficulty?")
        lines.append("A: Yes! You can switch to manual mode in the settings menu to")
        lines.append("   control speed, obstacles, and food spawn rate yourself.")
        lines.append("")
        lines.append("Q: Why is the game getting easier?")
        lines.append("A: The AI detected that you're struggling and is reducing the")
        lines.append("   difficulty to help you recover. Keep practicing!")
        lines.append("")
        lines.append("Q: How long does it take for difficulty to change?")
        lines.append("A: Difficulty changes happen smoothly over 2-3 seconds to avoid")
        lines.append("   jarring transitions.")
        lines.append("")
        lines.append("Q: Can I see my performance history?")
        lines.append("A: Yes! Check the statistics screen to see your best scores,")
        lines.append("   average survival times, and skill progression.")
        lines.append("")

        return "\n".join(lines)
