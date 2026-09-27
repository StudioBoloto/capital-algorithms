# ROS 2-контракт

## Вход

Узел подписывается на `sensor_msgs/msg/PointCloud2`. Требуются поля `x`, `y` и
`z`; поля `ring`, `intensity` и timestamp используются адаптером при наличии.
Имя входного топика задаётся параметром запуска.

## Выход

- `/metro_detector/obstacles_json` (`std_msgs/msg/String`) — подтверждённые
  кандидаты и диагностические поля;
- `/metro_detector/alarm` (`std_msgs/msg/Bool`) — наличие тревоги;
- `/metro_detector/nearest_obstacle_m` (`std_msgs/msg/Float32`) — расстояние до
  ближайшего кандидата, `NaN` при его отсутствии.

Координаты результата: `x` вправо, `y` вперёд, `z` вверх. Решение причинное и
не использует будущие кадры.

Каждый элемент `obstacles` содержит `center_xyz_m`, `size_xyz_m`,
`distance_forward_m`, `persistence_frames` и нормированный `confidence`.
`nearest_obstacle_m` в JSON равен `null`, когда подтверждённых препятствий нет;
одноимённый `Float32`-топик в этом случае содержит `NaN`.
