from django.http import HttpResponse

from selector.library.strava import save_refresh_token


def exchange_token(request):
    bare_minimum_scope = {"read", "activity:write", "activity:read_all"}
    code = request.GET.get("code")
    scope = request.GET.get("scope")
    scope_set = set(scope.split(","))
    is_min_scope = True
    for scope in bare_minimum_scope:
        if scope not in scope_set:
            is_min_scope = False

    save_refresh_token(code)
    # TODO: setup webhook

    if not is_min_scope:
        return HttpResponse("You're missing the minimum amount of permissions")

    return HttpResponse("You're signed up!")
