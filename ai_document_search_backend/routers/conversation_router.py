from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer

from ai_document_search_backend.container import Container
from ai_document_search_backend.services.auth_service import AuthService
from ai_document_search_backend.services.conversation_service import (
    Conversation,
    ConversationService,
)

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.get("")
@inject
def get_latest_conversation(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> Conversation:
    user = auth_service.get_current_user(token)
    return conversation_service.get_latest_conversation(user.username)


@router.post("")
@inject
def create_new_conversation(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> Conversation:
    user = auth_service.get_current_user(token)
    return conversation_service.create_new_conversation(user.username)


@router.delete("")
@inject
def clear_conversations(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> str:
    user = auth_service.get_current_user(token)
    return conversation_service.clear_conversations(user.username)
