from enum import EnumMeta, Enum


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

    @classmethod
    def has_name(cls, name):
        return name in cls.__members__

    @classmethod
    def has_value(cls, value):
        return value in cls


class Interaction(BaseEnum):
    like = "Like"
    share = "Share"
    repost = "Repost"
