#Django lib
from django.urls import path

#Internal libs
from views.ideas import (
    CreatePrivateIdea,
    CreatePublicIdea,
    ChangeEditorsPick,
    SearchBySymbol,
    SearchByTag,
    ShowIdea,
    SubmitRate,
    DeleteIdea,
    FeedIdeas,
    NewestIdeas,
    GetEditorsPickIdeas,
    GetTopIdeas,
    SaveScreenshot,
    DeleteScreenshot,
    SearchTag,
    CreateTag,
)

urlpatterns = [
    path("create_public_idea",CreatePublicIdea.as_view()),
    path("create_private_idea",CreatePrivateIdea.as_view()),
    path("show_idea",ShowIdea.as_view()),
    path("submit_rate",SubmitRate.as_view()),
    path("change_editors_pick",ChangeEditorsPick.as_view()),
    path("search_by_tag",SearchByTag.as_view()),
    path("search_by_symbol",SearchBySymbol.as_view()),
    path("delete_idea",DeleteIdea.as_view()),
    path("feed_ideas",FeedIdeas.as_view()),
    path("newest_ideas",NewestIdeas.as_view()),
    path("get_editors_pick",GetEditorsPickIdeas.as_view()),
    path("get_top_ideas",GetTopIdeas.as_view()),
    path("save_screenshot",SaveScreenshot.as_view()),
    path("delete_screenshot",DeleteScreenshot.as_view()),
    path("search_tag",SearchTag.as_view()),
    path("create_tag",CreateTag.as_view()),
]