import uuid
from typing import Any

from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService, Session

from study_coach.models.learning_session import LearningSession
from study_coach.models.student import StudentProfile

APP_NAME = "study_coach"


class LearningSessionService:
    """Manages student learning session state using Google ADK InMemorySessionService.

    Note:
        In-memory session storage is ephemeral and is not durable across
        application restarts. Production deployments would use DatabaseSessionService
        or VertexAiSessionService.
    """

    def __init__(
        self, adk_session_service: InMemorySessionService | None = None
    ) -> None:
        self._adk_service = adk_session_service or InMemorySessionService()

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: str,
        student_profile: StudentProfile | None = None,
        certification_name: str = "Google Cloud Generative AI Leader",
        days_remaining: int = 14,
    ) -> LearningSession:
        """Retrieves an existing LearningSession or initializes a new one."""
        existing = await self._adk_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

        if existing and existing.state and "learning_session" in existing.state:
            raw_state = existing.state["learning_session"]
            return LearningSession.from_adk_state(raw_state)

        # Initialize new LearningSession
        profile = student_profile or StudentProfile(
            experience_level="beginner",
            daily_study_minutes=90,
        )
        learning_session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            student_profile=profile,
            certification_name=certification_name,
            exam_deadline_or_days_remaining=days_remaining,
        )

        # Persist into ADK session
        await self.save_session(learning_session)
        return learning_session

    async def get_session(
        self, session_id: str, user_id: str
    ) -> LearningSession | None:
        """Retrieves a session if it exists."""
        adk_sess = await self._adk_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        if (
            not adk_sess
            or not adk_sess.state
            or "learning_session" not in adk_sess.state
        ):
            return None
        return LearningSession.from_adk_state(adk_sess.state["learning_session"])

    async def save_session(self, session: LearningSession) -> Session:
        """Persists the validated LearningSession into the ADK Session."""
        adk_state: dict[str, Any] = {"learning_session": session.to_adk_state()}

        # Check if ADK session exists
        existing = await self._adk_service.get_session(
            app_name=APP_NAME,
            user_id=session.user_id,
            session_id=session.session_id,
        )
        if existing:
            event = Event(
                id=str(uuid.uuid4()),
                author="system",
                actions=EventActions(state_delta=adk_state),
            )
            await self._adk_service.append_event(session=existing, event=event)
            return existing

        return await self._adk_service.create_session(
            app_name=APP_NAME,
            user_id=session.user_id,
            session_id=session.session_id,
            state=adk_state,
        )

    async def delete_session(self, session_id: str, user_id: str) -> None:
        """Deletes a session from in-memory storage."""
        await self._adk_service.delete_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
