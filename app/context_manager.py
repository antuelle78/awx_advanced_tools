# Context management and optimization for LLM conversations

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolCall:
    """Represents a tool call in the conversation."""

    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    timestamp: datetime
    success: bool
    response_time: float


@dataclass
class ConversationContext:
    """Manages conversation context for optimal LLM performance."""

    tool_calls: List[ToolCall]
    max_context_items: int
    context_summary_trigger: int
    model_name: str

    def __init__(
        self,
        model_name: str,
        max_context_items: int = 10,
        context_summary_trigger: int = 20,
    ):
        self.tool_calls: List[ToolCall] = []
        self.max_context_items = max_context_items
        self.context_summary_trigger = context_summary_trigger
        self.model_name = model_name
        self._summary: Optional[str] = None

    def add_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any,
        success: bool,
        response_time: float,
    ):
        """Add a tool call to the context."""
        tool_call = ToolCall(
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            timestamp=datetime.now(),
            success=success,
            response_time=response_time,
        )

        self.tool_calls.append(tool_call)

        # Prune old context if needed
        if len(self.tool_calls) > self.max_context_items:
            self._prune_context()

    def _prune_context(self):
        """Prune old context items to stay within limits."""
        # Keep the most recent items
        self.tool_calls = self.tool_calls[-self.max_context_items :]

    def get_recent_context(self, limit: Optional[int] = None) -> List[ToolCall]:
        """Get recent tool calls for context."""
        if limit is None:
            limit = self.max_context_items
        return self.tool_calls[-limit:]

    def get_context_summary(self) -> str:
        """Get a summary of the conversation context."""
        if len(self.tool_calls) < self.context_summary_trigger:
            return self._generate_recent_summary()

        if (
            self._summary is None or len(self.tool_calls) % 5 == 0
        ):  # Update summary periodically
            self._summary = self._generate_full_summary()

        return self._summary

    def _generate_recent_summary(self) -> str:
        """Generate summary of recent activity."""
        if not self.tool_calls:
            return "No previous tool calls."

        recent = self.get_recent_context(5)
        summary_parts = []

        for call in recent:
            status = "succeeded" if call.success else "failed"
            summary_parts.append(f"{call.tool_name} {status}")

        return f"Recent activity: {', '.join(summary_parts)}"

    def _generate_full_summary(self) -> str:
        """Generate comprehensive context summary."""
        if not self.tool_calls:
            return "No tool call history."

        # Group by tool type
        tool_counts: Dict[str, int] = {}
        success_rate: Dict[str, List[bool]] = {}

        for call in self.tool_calls:
            tool_counts[call.tool_name] = tool_counts.get(call.tool_name, 0) + 1
            if call.tool_name not in success_rate:
                success_rate[call.tool_name] = []
            success_rate[call.tool_name].append(call.success)

        # Calculate success rates
        summary_parts = []
        for tool, count in tool_counts.items():
            successes = sum(success_rate[tool])
            rate = successes / len(success_rate[tool]) * 100
            summary_parts.append(f"{tool}: {count} calls ({rate:.1f}% success)")

        return f"Conversation summary: {', '.join(summary_parts)}"

    def should_simplify_response(self) -> bool:
        """Determine if responses should be simplified based on context."""
        if len(self.tool_calls) < 3:
            return False

        # Check recent success rate
        recent_calls = self.get_recent_context(5)
        if not recent_calls:
            return False

        success_rate = sum(1 for call in recent_calls if call.success) / len(
            recent_calls
        )

        # Simplify if success rate is low (model struggling)
        return success_rate < 0.6

    def get_tool_usage_patterns(self) -> Dict[str, Any]:
        """Analyze tool usage patterns for optimization."""
        if not self.tool_calls:
            return {"total_calls": 0, "unique_tools": 0, "success_rate": 0.0}

        unique_tools = len(set(call.tool_name for call in self.tool_calls))
        total_calls = len(self.tool_calls)
        successful_calls = sum(1 for call in self.tool_calls if call.success)
        success_rate = successful_calls / total_calls if total_calls > 0 else 0.0

        # Most used tools
        tool_usage: Dict[str, int] = {}
        for call in self.tool_calls:
            tool_usage[call.tool_name] = tool_usage.get(call.tool_name, 0) + 1

        most_used = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "total_calls": total_calls,
            "unique_tools": unique_tools,
            "success_rate": success_rate,
            "most_used_tools": most_used,
            "average_response_time": sum(call.response_time for call in self.tool_calls)
            / total_calls,
        }

    def reset_context(self):
        """Reset conversation context."""
        self.tool_calls = []
        self._summary = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "tool_calls": [
                {
                    "tool_name": call.tool_name,
                    "parameters": call.parameters,
                    "result": str(call.result)[:500],  # Truncate long results
                    "timestamp": call.timestamp.isoformat(),
                    "success": call.success,
                    "response_time": call.response_time,
                }
                for call in self.tool_calls
            ],
            "max_context_items": self.max_context_items,
            "context_summary_trigger": self.context_summary_trigger,
            "model_name": self.model_name,
        }


class ContextManager:
    """Global context manager for multiple conversations."""

    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}

    def get_context(self, conversation_id: str, model_name: str) -> ConversationContext:
        """Get or create conversation context."""
        if conversation_id not in self.conversations:
            # Import here to avoid circular imports
            try:
                from app.model_capabilities import get_context_limits

                limits = get_context_limits(model_name)
                self.conversations[conversation_id] = ConversationContext(
                    model_name=model_name,
                    max_context_items=limits["max_context_items"],
                    context_summary_trigger=limits["context_summary_trigger"],
                )
            except ImportError:
                # Fallback limits
                self.conversations[conversation_id] = ConversationContext(
                    model_name=model_name
                )

        return self.conversations[conversation_id]

    def cleanup_old_contexts(self, max_conversations: int = 100):
        """Clean up old conversation contexts to prevent memory leaks."""
        if len(self.conversations) > max_conversations:
            # Remove oldest conversations (simple FIFO)
            conversations_to_remove = len(self.conversations) - max_conversations
            conversation_ids = list(self.conversations.keys())[:conversations_to_remove]

            for conv_id in conversation_ids:
                del self.conversations[conv_id]


# Global context manager instance
context_manager = ContextManager()
