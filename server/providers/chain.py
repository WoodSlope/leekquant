from __future__ import annotations

from typing import Any

from server.providers.mock_provider import MockProvider


AUTO_PROVIDER_NAMES = ("akshare", "sina")
REAL_PROVIDER_NAMES = {*AUTO_PROVIDER_NAMES}


def build_providers(provider_name: str = "auto"):
    warnings: list[str] = []
    if provider_name == "mock":
        return [MockProvider()], warnings
    if provider_name not in {"auto", *REAL_PROVIDER_NAMES}:
        warnings.append(f"未知数据源 {provider_name}，已降级到样本数据")
        return [MockProvider()], warnings

    names = AUTO_PROVIDER_NAMES if provider_name == "auto" else (provider_name,)
    providers = []
    for index, name in enumerate(names):
        provider = _try_create_provider(name, warnings, allow_next=index < len(names) - 1)
        if provider is not None:
            providers.append(provider)
    providers.append(MockProvider())
    return providers, warnings


def build_provider(provider_name: str = "auto"):
    providers, warnings = build_providers(provider_name)
    return providers[0], warnings


def call_provider_method(
    providers,
    warnings: list[str],
    method_name: str,
    *args: Any,
    action_label: str = "数据获取",
    **kwargs: Any,
):
    provider_list = providers if isinstance(providers, list) else [providers]
    for index, provider in enumerate(provider_list):
        try:
            return provider, getattr(provider, method_name)(*args, **kwargs)
        except Exception as exc:
            has_next_real_provider = any(item.name != "mock" for item in provider_list[index + 1 :])
            if provider.name == "mock":
                raise
            if has_next_real_provider:
                warnings.append(f"{provider.name} {action_label}失败，已尝试备用免费源: {exc}")
            else:
                warnings.append(f"{provider.name} {action_label}失败，已降级到样本数据: {exc}")

    fallback = MockProvider()
    return fallback, getattr(fallback, method_name)(*args, **kwargs)


def _try_create_provider(name: str, warnings: list[str], allow_next: bool):
    try:
        if name == "akshare":
            from server.providers.akshare_provider import AkshareProvider

            return AkshareProvider()
        if name == "sina":
            from server.providers.sina_provider import SinaProvider

            return SinaProvider()
    except Exception as exc:
        display_name = "AKShare" if name == "akshare" else "新浪"
        if allow_next:
            warnings.append(f"{display_name} 初始化失败，已尝试备用免费源: {exc}")
        else:
            warnings.append(f"{display_name} 初始化失败，已降级到样本数据: {exc}")
    return None
