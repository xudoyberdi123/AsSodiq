from rest_framework.permissions import IsAuthenticated
from starlette.responses import Response

from base.error_messages import MESSAGE, error_params_unfilled
from base.helper import CustomGenericAPIView, BearerAuth, custom_response


class CourseView(CustomGenericAPIView):
    authentication_classes = [BearerAuth]
    permission_classes = (IsAuthenticated,)

    def post(self, requests, *args, **kwargs):
        data = requests.data
        params = data.get('params')
        method = data.get("method")
        if not method:
            return Response(custom_response(status=False, message=MESSAGE['MethodMust']))

        if not params:
            return Response(custom_response(status=False, message=MESSAGE['ParamsMust']))

        nott = "email" if "email" not in params else "order_id" if "order_id" not in params else "amount" \
            if "amount" not in params else "action" if "action" not in params else None
        if nott:
            return Response(custom_response(status=False, message=error_params_unfilled(nott)))



