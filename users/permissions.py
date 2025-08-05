from enum import StrEnum


class CustomPermissionEnum(StrEnum):
    ADMIN = 'admin'
    CHAT = 'chat'


class PermissionEnum(StrEnum):
    ADD_POST = 'add_post'
    EDIT_POST = 'change_post'
    DELETE_POST = 'delete_post'
    FOLLOW_USER = 'follow_user'
    UNFOLLOW_USER = 'unfollow_user'
    CHANGE_PROFILE = 'change_profile'
    DELETE_PROFILE = 'delete_profile'
    ADD_COMMENT = 'add_comment'
    CHANGE_COMMENT = 'change_comment'
    DELETE_COMMENT = 'delete_comment'
    ADD_LIKE = 'add_like'
    DELETE_LIKE = 'delete_like'
    ADD_DISLIKE = 'add_dislike'
    DELETE_DISLIKE = 'delete_dislike'


class PermissionDescriptionEnum(StrEnum):
    ADD_POST = 'Can add post'
    EDIT_POST = 'Can change post'
    DELETE_POST = 'Can delete post'
    FOLLOW_USER = 'Can follow user'
    UNFOLLOW_USER = 'Can unfollow user'
    CHANGE_PROFILE = 'Can change profile'
    DELETE_PROFILE = 'Can delete profile'
    ADD_COMMENT = 'Can add comment'
    CHANGE_COMMENT = 'Can change comment'
    DELETE_COMMENT = 'Can delete comment'
    ADD_LIKE = 'Can add like'
    DELETE_LIKE = 'Can delete like'
    ADD_DISLIKE = 'Can add dislike'
    DELETE_DISLIKE = 'Can delete dislike'

