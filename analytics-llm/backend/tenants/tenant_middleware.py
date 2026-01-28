def resolve_tenant(request):
    return request.headers.get("X-Tenant-ID")
