import pytest

from src.core.transport import (
    DuplicateMessageError,
    Envelope,
    InMemoryDeduplicateMiddleware,
    InboundPipeline,
    Message,
    MessageDirection,
    NormalizeDefaultsMiddleware,
    OutboundPipeline,
    RoutingError,
    Router,
    SendResult,
    SenderNotFoundError,
    SenderRegistry,
    ValidationError,
    ValidateRequiredMiddleware,
)


@pytest.mark.asyncio
async def test_inbound_validate_required_fields():
    router = Router()
    inbound = InboundPipeline(router, [ValidateRequiredMiddleware()])
    message_missing = Message(channel=None, session_id=None, content="hi")

    with pytest.raises(ValidationError) as exc:
        await inbound.handle(message_missing)
    assert "缺少 session_id" in str(exc.value)

    invalid_role = Message(channel="c", session_id="s", role="invalid")
    with pytest.raises(ValidationError) as exc2:
        await inbound.handle(invalid_role)
    assert "不支持的角色" in str(exc2.value)


@pytest.mark.asyncio
async def test_inbound_deduplicate():
    router = Router()

    async def handler(ctx):
        return "ok"

    router.register("c1", handler)
    inbound = InboundPipeline(
        router,
        [InMemoryDeduplicateMiddleware(max_size=2), NormalizeDefaultsMiddleware(), ValidateRequiredMiddleware()],
    )

    msg = Message(id="m1", session_id="s1", channel="c1", content="hi")
    await inbound.handle(msg)

    with pytest.raises(DuplicateMessageError):
        await inbound.handle(Message(id="m1", session_id="s1", channel="c1", content="hi again"))


@pytest.mark.asyncio
async def test_route_hits_handler():
    called = {}

    async def handler(ctx):
        called["content"] = ctx.message.content
        return "ok"

    router = Router()
    router.register("console", handler)
    inbound = InboundPipeline(router, [NormalizeDefaultsMiddleware(), ValidateRequiredMiddleware()])

    result = await inbound.handle(Message(session_id="s", channel="console", content="hello"))
    assert result == "ok"
    assert called["content"] == "hello"


@pytest.mark.asyncio
async def test_route_missing_handler():
    router = Router()
    inbound = InboundPipeline(router, [NormalizeDefaultsMiddleware(), ValidateRequiredMiddleware()])

    with pytest.raises(RoutingError) as exc:
        await inbound.handle(Message(session_id="s", channel="nope", content="hello"))
    assert "未找到路由处理器" in str(exc.value)


@pytest.mark.asyncio
async def test_outbound_sender_registry():
    registry = SenderRegistry()
    outbound = OutboundPipeline(registry)

    with pytest.raises(SenderNotFoundError) as exc:
        await outbound.send(Message(session_id="s1", content="hi"))
    assert "缺少消息 channel" in str(exc.value)

    sent = {}

    async def sender(envelope: Envelope):
        sent["direction"] = envelope.direction
        sent["message_id"] = envelope.message.id
        return SendResult(success=True, detail="ok")

    registry.register("console", sender)
    result = await outbound.send(Message(session_id="s1", channel="console", content="yo"))

    assert sent["direction"] == MessageDirection.OUTBOUND
    assert sent["message_id"]
    assert result.success is True
