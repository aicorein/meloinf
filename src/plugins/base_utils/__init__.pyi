from .shares import onebot_app_name as _onebot_app_name
from .shares import onebot_app_ver as _onebot_app_ver
from .shares import onebot_id as _onebot_id
from .shares import onebot_name as _onebot_name
from .shares import onebot_other_infos as _onebot_other_infos
from .shares import onebot_protocol_ver as _onebot_protocol_ver
from .funcs import txt2img
from .funcs import wrap_s

onebot_app_name = _onebot_app_name.get()
onebot_app_ver = _onebot_app_ver.get()
onebot_id = _onebot_id.get()
onebot_name = _onebot_name.get()
onebot_other_infos = _onebot_other_infos.get()
onebot_protocol_ver = _onebot_protocol_ver.get()

__all__ = ('onebot_app_name', 'onebot_app_ver', 'onebot_id', 'onebot_name', 'onebot_other_infos', 'onebot_protocol_ver', 'txt2img', 'wrap_s')