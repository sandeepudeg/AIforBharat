"""
Difficulty Change Notification System
Displays notifications when difficulty parameters change, indicating which parameter changed and why
Requirements: 3.2
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from game_types import DifficultyLevel


@dataclass
class DifficultyChangeNotification:
    """Represents a single difficulty change notification"""
    parameter: str  # 'speed', 'obstacle_density', 'food_spawn_rate', or 'level'
    old_value: float
    new_value: float
    reason: str  # Explanation for the change
    timestamp: float
    duration_ms: int = 3000  # Display duration in milliseconds


class DifficultyChangeNotificationSystem:
    """Manages difficulty change notifications"""

    def __init__(self):
        """Initialize the notification system"""
        self.notifications: list[DifficultyChangeNotification] = []
        self.active_notification: Optional[DifficultyChangeNotification] = None
        self.notification_start_time: Optional[float] = None

    def detect_changes(
        self,
        old_difficulty: DifficultyLevel,
        new_difficulty: DifficultyLevel,
        reason: str = ""
    ) -> list[DifficultyChangeNotification]:
        """
        Detect changes between two difficulty levels and create notifications
        Returns list of notifications for each parameter that changed
        """
        changes = []
        current_time = datetime.now().timestamp()

        # Check speed change
        if old_difficulty.speed != new_difficulty.speed:
            change = DifficultyChangeNotification(
                parameter='speed',
                old_value=old_difficulty.speed,
                new_value=new_difficulty.speed,
                reason=reason or self._generate_speed_reason(
                    old_difficulty.speed,
                    new_difficulty.speed
                ),
                timestamp=current_time
            )
            changes.append(change)

        # Check obstacle density change
        if old_difficulty.obstacle_density != new_difficulty.obstacle_density:
            change = DifficultyChangeNotification(
                parameter='obstacle_density',
                old_value=old_difficulty.obstacle_density,
                new_value=new_difficulty.obstacle_density,
                reason=reason or self._generate_obstacle_reason(
                    old_difficulty.obstacle_density,
                    new_difficulty.obstacle_density
                ),
                timestamp=current_time
            )
            changes.append(change)

        # Check food spawn rate change
        if old_difficulty.food_spawn_rate != new_difficulty.food_spawn_rate:
            change = DifficultyChangeNotification(
                parameter='food_spawn_rate',
                old_value=old_difficulty.food_spawn_rate,
                new_value=new_difficulty.food_spawn_rate,
                reason=reason or self._generate_spawn_rate_reason(
                    old_difficulty.food_spawn_rate,
                    new_difficulty.food_spawn_rate
                ),
                timestamp=current_time
            )
            changes.append(change)

        # Check overall level change
        if old_difficulty.level != new_difficulty.level:
            change = DifficultyChangeNotification(
                parameter='level',
                old_value=old_difficulty.level,
                new_value=new_difficulty.level,
                reason=reason or self._generate_level_reason(
                    old_difficulty.level,
                    new_difficulty.level
                ),
                timestamp=current_time
            )
            changes.append(change)

        # Store notifications
        self.notifications.extend(changes)

        # Set first notification as active if available
        if changes and not self.active_notification:
            self.active_notification = changes[0]
            self.notification_start_time = current_time

        return changes

    def _generate_speed_reason(self, old_speed: int, new_speed: int) -> str:
        """Generate reason text for speed change"""
        if new_speed > old_speed:
            return "You're playing well! Speed increased."
        else:
            return "Let's slow things down a bit."

    def _generate_obstacle_reason(self, old_density: int, new_density: int) -> str:
        """Generate reason text for obstacle density change"""
        if new_density > old_density:
            return "More obstacles added for extra challenge!"
        else:
            return "Fewer obstacles to help you recover."

    def _generate_spawn_rate_reason(self, old_rate: float, new_rate: float) -> str:
        """Generate reason text for food spawn rate change"""
        if new_rate > old_rate:
            return "More food available to keep you going!"
        else:
            return "Food is more scarce now."

    def _generate_level_reason(self, old_level: int, new_level: int) -> str:
        """Generate reason text for overall level change"""
        if new_level > old_level:
            return f"Difficulty increased to level {new_level}!"
        else:
            return f"Difficulty decreased to level {new_level}."

    def get_active_notification(self) -> Optional[DifficultyChangeNotification]:
        """Get the currently active notification"""
        return self.active_notification

    def get_notification_display(self) -> str:
        """Get formatted display string for active notification"""
        if not self.active_notification:
            return ""

        notif = self.active_notification
        param_display = self._format_parameter_name(notif.parameter)
        return f"[{param_display}] {notif.old_value} → {notif.new_value}: {notif.reason}"

    def _format_parameter_name(self, parameter: str) -> str:
        """Format parameter name for display"""
        if parameter == 'speed':
            return "Speed"
        elif parameter == 'obstacle_density':
            return "Obstacles"
        elif parameter == 'food_spawn_rate':
            return "Food Rate"
        elif parameter == 'level':
            return "Level"
        return parameter

    def advance_notification(self, current_time: float) -> bool:
        """
        Advance to next notification if current one has expired
        Returns True if there are more notifications to display
        """
        if not self.active_notification or not self.notification_start_time:
            return False

        elapsed_ms = (current_time - self.notification_start_time) * 1000
        if elapsed_ms > self.active_notification.duration_ms:
            # Find next unshown notification
            current_idx = self.notifications.index(self.active_notification)
            if current_idx + 1 < len(self.notifications):
                self.active_notification = self.notifications[current_idx + 1]
                self.notification_start_time = current_time
                return True
            else:
                self.active_notification = None
                self.notification_start_time = None
                return False

        return True

    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notifications = []
        self.active_notification = None
        self.notification_start_time = None

    def get_all_notifications(self) -> list[DifficultyChangeNotification]:
        """Get all recorded notifications"""
        return self.notifications.copy()

    def get_notification_count(self) -> int:
        """Get total number of notifications"""
        return len(self.notifications)

    def is_notification_active(self) -> bool:
        """Check if there's an active notification"""
        return self.active_notification is not None
