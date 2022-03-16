from django.http import HttpResponse
from django.shortcuts import render

from selector.library.strava import save_refresh_token


def exchange_token(request):
    code = request.GET.get("code")
    scope = request.GET.get("scope")
    scope_set = set(scope.split(","))
    # TODO: check that if we request read_all we have an option to lower permissions
    read_set = {"activity:read", "activity:read_all"}
    if len(read_set.intersection(scope_set)) == 0:
        return HttpResponse(
            "We need to be able to read activities to determine future rides."
        )
    elif "activity:write" not in scope_set:
        return HttpResponse(
            "We need to be able to write activities to change your gear after the fact"
        )

    save_refresh_token(code)

    return render(request, "exchange_token/index.html")
