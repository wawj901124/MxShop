from six.moves.urllib_parse import quote
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler   #导入 jwt_encode_handler,jwt_payload_handler ，返回token用

from .utils import sanitize_redirect, user_is_authenticated, \
                   user_is_active, partial_pipeline_data, setting_url


def do_auth(backend, redirect_name='next'):
    # Save any defined next value into session
    data = backend.strategy.request_data(merge=False)

    # Save extra data into session.
    for field_name in backend.setting('FIELDS_STORED_IN_SESSION', []):
        if field_name in data:
            backend.strategy.session_set(field_name, data[field_name])

    if redirect_name in data:
        # Check and sanitize a user-defined GET/POST next field value
        redirect_uri = data[redirect_name]
        if backend.setting('SANITIZE_REDIRECTS', True):
            allowed_hosts = backend.setting('ALLOWED_REDIRECT_HOSTS', []) + \
                            [backend.strategy.request_host()]
            redirect_uri = sanitize_redirect(allowed_hosts, redirect_uri)
        backend.strategy.session_set(
            redirect_name,
            redirect_uri or backend.setting('LOGIN_REDIRECT_URL')
        )
    return backend.start()


def do_complete(backend, login, user=None, redirect_name='next',
                *args, **kwargs):
    data = backend.strategy.request_data()

    is_authenticated = user_is_authenticated(user)
    user = user if is_authenticated else None

    partial = partial_pipeline_data(backend, user, *args, **kwargs)
    if partial:
        user = backend.continue_pipeline(partial)
        # clean partial data after usage
        backend.strategy.clean_partial_pipeline(partial.token)
    else:
        user = backend.complete(user=user, *args, **kwargs)

    # pop redirect value before the session is trashed on login(), but after
    # the pipeline so that the pipeline can change the redirect if needed
    redirect_value = backend.strategy.session_get(redirect_name, '') or \
                     data.get(redirect_name, '')

    # check if the output value is something else than a user and just
    # return it to the client
    user_model = backend.strategy.storage.user.user_model()
    if user and not isinstance(user, user_model):
        return user

    if is_authenticated:
        if not user:
            url = setting_url(backend, redirect_value, 'LOGIN_REDIRECT_URL')
        else:
            url = setting_url(backend, redirect_value,
                              'NEW_ASSOCIATION_REDIRECT_URL',
                              'LOGIN_REDIRECT_URL')
    elif user:
        if user_is_active(user):
            # catch is_new/social_user in case login() resets the instance
            is_new = getattr(user, 'is_new', False)
            social_user = user.social_user
            login(backend, user, social_user)
            # store last login backend name in session
            backend.strategy.session_set('social_auth_last_login_backend',
                                         social_user.provider)

            if is_new:
                url = setting_url(backend,
                                  'NEW_USER_REDIRECT_URL',
                                  redirect_value,
                                  'LOGIN_REDIRECT_URL')
            else:
                url = setting_url(backend, redirect_value,
                                  'LOGIN_REDIRECT_URL')
        else:
            if backend.setting('INACTIVE_USER_LOGIN', False):
                social_user = user.social_user
                login(backend, user, social_user)
            url = setting_url(backend, 'INACTIVE_USER_URL', 'LOGIN_ERROR_URL',
                              'LOGIN_URL')
    else:
        url = setting_url(backend, 'LOGIN_ERROR_URL', 'LOGIN_URL')

    if redirect_value and redirect_value != url:
        redirect_value = quote(redirect_value)
        url += ('&' if '?' in url else '?') + \
               '{0}={1}'.format(redirect_name, redirect_value)

    if backend.setting('SANITIZE_REDIRECTS', True):
        allowed_hosts = backend.setting('ALLOWED_REDIRECT_HOSTS', []) + \
                        [backend.strategy.request_host()]
        url = sanitize_redirect(allowed_hosts, url) or \
              backend.setting('LOGIN_REDIRECT_URL')
    response = backend.strategy.redirect(url)   #设置backend.strategy.redirect(url) 为一个response
    payload = jwt_payload_handler(user)  # 重写payload ,传递一个user
    # re_dict["token"] = jwt_encode_handler(payload)  # 将re_dict中的token赋值jwt_encode_handler(payload)
    # re_dict["name"] = user.name if user.name else user.username  # 如果user中有name,则将user模块中name值赋值给re_dict中的"name"
    # 否则就将user模块中的username值赋值给re_dict中的"name"
    response.set_cookie("name",user.name if user.name else user.username,max,max_age=24*3600 )    #设置cookie中name字段内容,
                                                                                    # 设置一个过期时间为：24*3600秒，即1天,一定要设置一个过期时间
    response.set_cookie("token", jwt_encode_handler(payload),max_age=24*3600)  #设置cookie中token字段内容
                                                                                    # 设置一个过期时间为：24*3600秒，即1天，一定要设置一个过期时间
    return response   #返回cookie带有name和token的url
    # return backend.strategy.redirect(url)


def do_disconnect(backend, user, association_id=None, redirect_name='next',
                  *args, **kwargs):
    partial = partial_pipeline_data(backend, user, *args, **kwargs)
    if partial:
        if association_id and not partial.kwargs.get('association_id'):
            partial.extend_kwargs({
                'association_id': association_id
            })
        response = backend.disconnect(*partial.args, **partial.kwargs)
        # clean partial data after usage
        backend.strategy.clean_partial_pipeline(partial.token)
    else:
        response = backend.disconnect(user=user, association_id=association_id,
                                      *args, **kwargs)

    if isinstance(response, dict):
        url = backend.strategy.absolute_uri(
            backend.strategy.request_data().get(redirect_name, '') or
            backend.setting('DISCONNECT_REDIRECT_URL') or
            backend.setting('LOGIN_REDIRECT_URL')
        )
        if backend.setting('SANITIZE_REDIRECTS', True):
            allowed_hosts = backend.setting('ALLOWED_REDIRECT_HOSTS', []) + \
                            [backend.strategy.request_host()]
            url = sanitize_redirect(allowed_hosts, url) or \
                backend.setting('DISCONNECT_REDIRECT_URL') or \
                backend.setting('LOGIN_REDIRECT_URL')
        response = backend.strategy.redirect(url)
    return response
