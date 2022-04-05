"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor = ...

class KnowledgeBoxResponseStatus(_KnowledgeBoxResponseStatus, metaclass=_KnowledgeBoxResponseStatusEnumTypeWrapper):
    pass
class _KnowledgeBoxResponseStatus:
    V = typing.NewType('V', builtins.int)
class _KnowledgeBoxResponseStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_KnowledgeBoxResponseStatus.V], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
    OK = KnowledgeBoxResponseStatus.V(0)
    CONFLICT = KnowledgeBoxResponseStatus.V(1)
    NOTFOUND = KnowledgeBoxResponseStatus.V(2)
    ERROR = KnowledgeBoxResponseStatus.V(3)

OK = KnowledgeBoxResponseStatus.V(0)
CONFLICT = KnowledgeBoxResponseStatus.V(1)
NOTFOUND = KnowledgeBoxResponseStatus.V(2)
ERROR = KnowledgeBoxResponseStatus.V(3)
global___KnowledgeBoxResponseStatus = KnowledgeBoxResponseStatus


class KnowledgeBoxID(google.protobuf.message.Message):
    """ID

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    SLUG_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    slug: typing.Text = ...
    uuid: typing.Text = ...
    def __init__(self,
        *,
        slug : typing.Text = ...,
        uuid : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["slug",b"slug","uuid",b"uuid"]) -> None: ...
global___KnowledgeBoxID = KnowledgeBoxID

class KnowledgeBox(google.protobuf.message.Message):
    """GET

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    SLUG_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    CONFIG_FIELD_NUMBER: builtins.int
    slug: typing.Text = ...
    uuid: typing.Text = ...
    status: global___KnowledgeBoxResponseStatus.V = ...
    @property
    def config(self) -> global___KnowledgeBoxConfig: ...
    def __init__(self,
        *,
        slug : typing.Text = ...,
        uuid : typing.Text = ...,
        status : global___KnowledgeBoxResponseStatus.V = ...,
        config : typing.Optional[global___KnowledgeBoxConfig] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["config",b"config"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["config",b"config","slug",b"slug","status",b"status","uuid",b"uuid"]) -> None: ...
global___KnowledgeBox = KnowledgeBox

class KnowledgeBoxConfig(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    TITLE_FIELD_NUMBER: builtins.int
    DESCRIPTION_FIELD_NUMBER: builtins.int
    ENABLED_FILTERS_FIELD_NUMBER: builtins.int
    ENABLED_INSIGHTS_FIELD_NUMBER: builtins.int
    SLUG_FIELD_NUMBER: builtins.int
    title: typing.Text = ...
    description: typing.Text = ...
    @property
    def enabled_filters(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    @property
    def enabled_insights(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    slug: typing.Text = ...
    def __init__(self,
        *,
        title : typing.Text = ...,
        description : typing.Text = ...,
        enabled_filters : typing.Optional[typing.Iterable[typing.Text]] = ...,
        enabled_insights : typing.Optional[typing.Iterable[typing.Text]] = ...,
        slug : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["description",b"description","enabled_filters",b"enabled_filters","enabled_insights",b"enabled_insights","slug",b"slug","title",b"title"]) -> None: ...
global___KnowledgeBoxConfig = KnowledgeBoxConfig

class KnowledgeBoxNew(google.protobuf.message.Message):
    """NEW

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    SLUG_FIELD_NUMBER: builtins.int
    CONFIG_FIELD_NUMBER: builtins.int
    FORCEUUID_FIELD_NUMBER: builtins.int
    slug: typing.Text = ...
    @property
    def config(self) -> global___KnowledgeBoxConfig: ...
    forceuuid: typing.Text = ...
    def __init__(self,
        *,
        slug : typing.Text = ...,
        config : typing.Optional[global___KnowledgeBoxConfig] = ...,
        forceuuid : typing.Text = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["config",b"config"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["config",b"config","forceuuid",b"forceuuid","slug",b"slug"]) -> None: ...
global___KnowledgeBoxNew = KnowledgeBoxNew

class NewKnowledgeBoxResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    STATUS_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    status: global___KnowledgeBoxResponseStatus.V = ...
    uuid: typing.Text = ...
    def __init__(self,
        *,
        status : global___KnowledgeBoxResponseStatus.V = ...,
        uuid : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["status",b"status","uuid",b"uuid"]) -> None: ...
global___NewKnowledgeBoxResponse = NewKnowledgeBoxResponse

class KnowledgeBoxPrefix(google.protobuf.message.Message):
    """SEARCH / LIST

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    PREFIX_FIELD_NUMBER: builtins.int
    prefix: typing.Text = ...
    def __init__(self,
        *,
        prefix : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["prefix",b"prefix"]) -> None: ...
global___KnowledgeBoxPrefix = KnowledgeBoxPrefix

class KnowledgeBoxUpdate(google.protobuf.message.Message):
    """UPDATE

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    SLUG_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    CONFIG_FIELD_NUMBER: builtins.int
    slug: typing.Text = ...
    uuid: typing.Text = ...
    @property
    def config(self) -> global___KnowledgeBoxConfig: ...
    def __init__(self,
        *,
        slug : typing.Text = ...,
        uuid : typing.Text = ...,
        config : typing.Optional[global___KnowledgeBoxConfig] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["config",b"config"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["config",b"config","slug",b"slug","uuid",b"uuid"]) -> None: ...
global___KnowledgeBoxUpdate = KnowledgeBoxUpdate

class UpdateKnowledgeBoxResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    STATUS_FIELD_NUMBER: builtins.int
    UUID_FIELD_NUMBER: builtins.int
    status: global___KnowledgeBoxResponseStatus.V = ...
    uuid: typing.Text = ...
    def __init__(self,
        *,
        status : global___KnowledgeBoxResponseStatus.V = ...,
        uuid : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["status",b"status","uuid",b"uuid"]) -> None: ...
global___UpdateKnowledgeBoxResponse = UpdateKnowledgeBoxResponse

class GCKnowledgeBoxResponse(google.protobuf.message.Message):
    """GC

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    def __init__(self,
        ) -> None: ...
global___GCKnowledgeBoxResponse = GCKnowledgeBoxResponse

class DeleteKnowledgeBoxResponse(google.protobuf.message.Message):
    """DELETE

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    STATUS_FIELD_NUMBER: builtins.int
    status: global___KnowledgeBoxResponseStatus.V = ...
    def __init__(self,
        *,
        status : global___KnowledgeBoxResponseStatus.V = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["status",b"status"]) -> None: ...
global___DeleteKnowledgeBoxResponse = DeleteKnowledgeBoxResponse

class Label(google.protobuf.message.Message):
    """Labels on a Knowledge Box

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    TITLE_FIELD_NUMBER: builtins.int
    RELATED_FIELD_NUMBER: builtins.int
    TEXT_FIELD_NUMBER: builtins.int
    URI_FIELD_NUMBER: builtins.int
    title: typing.Text = ...
    related: typing.Text = ...
    text: typing.Text = ...
    uri: typing.Text = ...
    def __init__(self,
        *,
        title : typing.Text = ...,
        related : typing.Text = ...,
        text : typing.Text = ...,
        uri : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["related",b"related","text",b"text","title",b"title","uri",b"uri"]) -> None: ...
global___Label = Label

class LabelSet(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    TITLE_FIELD_NUMBER: builtins.int
    COLOR_FIELD_NUMBER: builtins.int
    LABELS_FIELD_NUMBER: builtins.int
    title: typing.Text = ...
    color: typing.Text = ...
    @property
    def labels(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Label]: ...
    def __init__(self,
        *,
        title : typing.Text = ...,
        color : typing.Text = ...,
        labels : typing.Optional[typing.Iterable[global___Label]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["color",b"color","labels",b"labels","title",b"title"]) -> None: ...
global___LabelSet = LabelSet

class Labels(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class LabelsetEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text = ...
        @property
        def value(self) -> global___LabelSet: ...
        def __init__(self,
            *,
            key : typing.Text = ...,
            value : typing.Optional[global___LabelSet] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    LABELSET_FIELD_NUMBER: builtins.int
    @property
    def labelset(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___LabelSet]: ...
    def __init__(self,
        *,
        labelset : typing.Optional[typing.Mapping[typing.Text, global___LabelSet]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["labelset",b"labelset"]) -> None: ...
global___Labels = Labels

class Entity(google.protobuf.message.Message):
    """Entities on a Knowledge Box

    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    VALUE_FIELD_NUMBER: builtins.int
    MERGED_FIELD_NUMBER: builtins.int
    REPRESENTS_FIELD_NUMBER: builtins.int
    value: typing.Text = ...
    merged: builtins.bool = ...
    @property
    def represents(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        value : typing.Text = ...,
        merged : builtins.bool = ...,
        represents : typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["merged",b"merged","represents",b"represents","value",b"value"]) -> None: ...
global___Entity = Entity

class EntitiesGroup(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class EntitiesEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text = ...
        @property
        def value(self) -> global___Entity: ...
        def __init__(self,
            *,
            key : typing.Text = ...,
            value : typing.Optional[global___Entity] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    ENTITIES_FIELD_NUMBER: builtins.int
    TITLE_FIELD_NUMBER: builtins.int
    COLOR_FIELD_NUMBER: builtins.int
    @property
    def entities(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___Entity]: ...
    title: typing.Text = ...
    color: typing.Text = ...
    def __init__(self,
        *,
        entities : typing.Optional[typing.Mapping[typing.Text, global___Entity]] = ...,
        title : typing.Text = ...,
        color : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["color",b"color","entities",b"entities","title",b"title"]) -> None: ...
global___EntitiesGroup = EntitiesGroup

class Widget(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class WidgetMode(_WidgetMode, metaclass=_WidgetModeEnumTypeWrapper):
        pass
    class _WidgetMode:
        V = typing.NewType('V', builtins.int)
    class _WidgetModeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_WidgetMode.V], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
        BUTTON = Widget.WidgetMode.V(0)
        INPUT = Widget.WidgetMode.V(1)
        FORM = Widget.WidgetMode.V(2)

    BUTTON = Widget.WidgetMode.V(0)
    INPUT = Widget.WidgetMode.V(1)
    FORM = Widget.WidgetMode.V(2)

    class WidgetFeatures(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        USEFILTERS_FIELD_NUMBER: builtins.int
        SUGGESTENTITIES_FIELD_NUMBER: builtins.int
        SUGGESTSENTENCES_FIELD_NUMBER: builtins.int
        SUGGESTPARAGRAPHS_FIELD_NUMBER: builtins.int
        useFilters: builtins.bool = ...
        suggestEntities: builtins.bool = ...
        suggestSentences: builtins.bool = ...
        suggestParagraphs: builtins.bool = ...
        def __init__(self,
            *,
            useFilters : builtins.bool = ...,
            suggestEntities : builtins.bool = ...,
            suggestSentences : builtins.bool = ...,
            suggestParagraphs : builtins.bool = ...,
            ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["suggestEntities",b"suggestEntities","suggestParagraphs",b"suggestParagraphs","suggestSentences",b"suggestSentences","useFilters",b"useFilters"]) -> None: ...

    class StyleEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text = ...
        value: typing.Text = ...
        def __init__(self,
            *,
            key : typing.Text = ...,
            value : typing.Text = ...,
            ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    ID_FIELD_NUMBER: builtins.int
    DESCRIPTION_FIELD_NUMBER: builtins.int
    MODE_FIELD_NUMBER: builtins.int
    FEATURES_FIELD_NUMBER: builtins.int
    FILTERS_FIELD_NUMBER: builtins.int
    TOPENTITIES_FIELD_NUMBER: builtins.int
    STYLE_FIELD_NUMBER: builtins.int
    id: typing.Text = ...
    description: typing.Text = ...
    mode: global___Widget.WidgetMode.V = ...
    @property
    def features(self) -> global___Widget.WidgetFeatures: ...
    @property
    def filters(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    @property
    def topEntities(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    @property
    def style(self) -> google.protobuf.internal.containers.ScalarMap[typing.Text, typing.Text]: ...
    def __init__(self,
        *,
        id : typing.Text = ...,
        description : typing.Text = ...,
        mode : global___Widget.WidgetMode.V = ...,
        features : typing.Optional[global___Widget.WidgetFeatures] = ...,
        filters : typing.Optional[typing.Iterable[typing.Text]] = ...,
        topEntities : typing.Optional[typing.Iterable[typing.Text]] = ...,
        style : typing.Optional[typing.Mapping[typing.Text, typing.Text]] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["features",b"features"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["description",b"description","features",b"features","filters",b"filters","id",b"id","mode",b"mode","style",b"style","topEntities",b"topEntities"]) -> None: ...
global___Widget = Widget
