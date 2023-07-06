import coreapi
import coreschema
from rest_framework.schemas import AutoSchema, ManualSchema

from blogging.enums import Interaction

PostInteractionViewSetSchema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="post",
                location='form',            # possible values: path, query, body, form
                required=True,
                schema=coreschema.Integer(description="post/comment ID to interact with"),
                type=int,
                description='',
                example='',
            ),
            coreapi.Field(
                name="activity",
                location='form',            # possible values: path, query, body, form
                required=True,
                schema=coreschema.Enum(description="action to be performed",
                                       enum=Interaction.names()),
                type=str,
                description='',
                example='',
            ),
        ]
    )

FollowUserViewSchema = ManualSchema(
        fields=[
            coreapi.Field(
                name="user_id",
                location='form',            # possible values: path, query, body, form
                required=True,
                schema=coreschema.Integer(description="user id to follow"),
                type=int,
                description='{"user_id": int}',
                example='',
            ),
        ],
        encoding='application/json'
    )

TimelineViewSchema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="update_cache",
                location='query',            # possible values: path, query, body, form
                required=False,
                schema=coreschema.Boolean(description="whether to force update cache"),
                type=bool,
                description='',
                example='',
            ),
        ]
    )
