from django.urls import path

from ideas.views import (
    CreatePrivateIdea,
    CreatePublicIdea,
    ChangeEditorsPick,
    Search,
    ShowIdea,
    SubmitRate,
    DeleteIdea,
    FeedIdeas,
    NewestIdeas,
    GetEditorsPickIdeas,
    GetTopIdeas,
)

urlpatterns = [
    path("create_public_idea",CreatePublicIdea.as_view()),
    path("create_private_idea",CreatePrivateIdea.as_view()),
    path("show_idea",ShowIdea.as_view()),
    path("submit_rate",SubmitRate.as_view()),
    path("change_editors_pick",ChangeEditorsPick.as_view()),
    path("search",Search.as_view()),
    path("delete_idea",DeleteIdea.as_view()),
    path("feed_ideas",FeedIdeas.as_view()),
    path("newest_ideas",NewestIdeas.as_view()),
    path("get_editors_pick",GetEditorsPickIdeas.as_view()),
    path("get_top_ideas",GetTopIdeas.as_view()),
]