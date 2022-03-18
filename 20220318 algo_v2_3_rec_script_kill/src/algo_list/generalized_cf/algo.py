import random
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn import preprocessing

from database import DataBase


def _choose_contents(user_id: str, set_attr: str, behavior: str, obj_attr: str, contents_from: set, data_base: DataBase) -> set:
    """
    从与用户X相关的集合中获取内容，得到集合
    :param user_id: 用户X的id
    :param set_attr:遍历集合的主体，包括user和club
    :param behavior: 遍历集合的主体的行为
    :param obj_attr: 遍历集合的客体，包括item和selected_item
    :param contents_from: 需要遍历的集合
    :param data_base: 类数据库类的实例
    :return: 得到的内容集合
    """
    yi = set()

    # 遍历集合contents_from
    for i in contents_from:
        yi = yi | set(data_base.get_objs([set_attr, i, behavior, obj_attr], key="动态"))

    return yi


def _join_contents_set(a: set, n_a: int, b: set, n_b: int, threshold: int) -> [set, int]:
    """
    将集合a的元素部分或全部加入到b集，得到c集
    :param a: a集
    :param n_a: a集的元素个数
    :param b: b集,代表alpha或beta集
    :param n_b: b集的元素个数
    :param threshold: c集的元素个数阈值
    :return: c集和元素个数n_c
    """
    if n_a + n_b <= threshold:
        c = b | a
    else:
        a_ = set(random.sample(list(a), k=threshold-n_b))
        c = b | a_

    n_c = len(c)

    return [c, n_c]


def _join_contents_list(a: list, n_a: int, b: list, n_b: int, threshold: int) -> [list, int]:
    """
    将列表a的元素部分或全部加入到列表b的末尾，得到列表c
    :param a: 列表a
    :param n_a: 列表a的元素个数
    :param b: 列表b
    :param n_b: 列表b的元素个数
    :param threshold: 列表c的元素个数阈值
    :return: 列表c和元素个数n_c
    """
    if n_a + n_b <= threshold:
        c = b + a
    else:
        a_ = random.sample(list(a), k=threshold-n_b)
        c = b + a_

    n_c = len(c)

    return [c, n_c]


def _sort_items(user_vec: np.ndarray, item_inv_mapper: dict, x: np.ndarray, k: int, metric='cosine', show_distance=False) -> list:
    """
    使用余弦相似度对召回集进行排序
    :param user_vec: 用户特征向量
    :param item_inv_mapper: 物品反映射表
    :param x: 召回集物品的所有特征向量形成的2d矩阵
    :param k: 近邻的个数
    :param metric: 比较的量度
    :param show_distance: 是否显示与近邻的距离
    :return: 经过knn排序后的召回集
    """

    neighbour_ids = []

    knn = NearestNeighbors(n_neighbors=k, metric=metric)
    knn.fit(x)
    if isinstance(user_vec, np.ndarray):
        user_vec = user_vec.reshape(1, -1)
    neighbour = knn.kneighbors(user_vec, return_distance=show_distance)
    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(item_inv_mapper[n])
    return neighbour_ids


def _prefilter(user_id: str, train_data: list, data_base: DataBase, test_flag: bool):
    """
    初筛过滤算法
    :param user_id: 用户ID
    :param train_data:所有用户点赞的训练物品集
    :param data_base: 类数据库类的实例
    :param test_flag:是否测试
    :return: alpha（召回集）和元素个数n_alpha
    """
    alpha = set()  # 初始化集合alpha为空
    y = set(data_base.get_objs(['user', user_id, 'follow', 'user']))  # 关注用户集合
    clubs = set(data_base.get_objs(['user', user_id, 'join', 'club'], key="动态"))  # 所属的Club集合
    # print("start prefilter")

    thresholds = [50, 90, 100]

    # 取每个用户点赞的内容
    if test_flag:
        c_yi = set()
        for i in y:
            if i in train_data.keys():
                c_yi = c_yi | set(train_data[i])
    else:
        c_yi = set(_choose_contents(user_id, 'user', 'like', 'item', y, data_base))

    alpha = alpha | c_yi
    n_alpha = len(alpha)

    if n_alpha < thresholds[0]:
        # 取每个用户点击的内容
        d_yi = set(_choose_contents(user_id, 'user', 'view', 'item', y, data_base))
        n_d_yi = len(d_yi)
        alpha, n_alpha = _join_contents_set(d_yi, n_d_yi, alpha, n_alpha, thresholds[0])
    else:
        alpha = set(random.sample(list(alpha), k=thresholds[0]))
        n_alpha = len(alpha)

    # 取集合CLUB的所有内容精选
    e_club = set(_choose_contents(user_id, 'club', 'have', 'selected_item', clubs, data_base))
    n_e_club = len(e_club)
    [alpha, n_alpha] = _join_contents_set(e_club, n_e_club, alpha, n_alpha, thresholds[1])

    # 取集合CLUB的补集的所有内容精选
    e_club_ = set(_choose_contents(user_id, 'club', 'have', 'selected_item', set(data_base.clubs) - clubs, data_base))
    n_e_club_ = len(e_club_)
    [alpha, n_alpha] = _join_contents_set(e_club_, n_e_club_, alpha, n_alpha, thresholds[2])

    # 去掉用户x已点赞，点击或曝光的内容
    if test_flag:
        alpha -= set(train_data[user_id])
    else:
        alpha -= set(data_base.get_objs(['user', user_id, 'like', 'item'], key="动态"))
    alpha -= set(data_base.get_objs(['user', user_id, 'view', 'item'], key="动态"))
    alpha -= set(data_base.get_objs(['user', user_id, 'create', 'item'], key="动态"))
    n_alpha = len(alpha)

    if n_alpha > thresholds[2]:
        raise ValueError(f"输出召回集alpha的长度错误，大于{thresholds[2]}")
    # print("召回集alpha的长度为：{}".format(n_alpha))
    return alpha, n_alpha


def _machine_sorting(user_id: str, alpha: set, n_alpha: int, train_data: list, data_base_: DataBase, test_flag: bool):
    """
    机器排序算法
    :param user_id: 用户ID
    :param alpha: 初筛过滤得到的召回集
    :param n_alpha: 召回集alpha的元素个数
    :param train_data:所有用户点赞的训练物品集
    :param data_base_: 类数据库类的实例
    :param test_flag:是否测试
    :return: 对alpha排序得到的beta（推荐集）
    """
    if not alpha:
        raise ValueError(f"输入召回集alpha为空")

    # 选取用户最近点赞的不多于100条内容得到用户的特征向量
    if test_flag:
        user_like = train_data[str(user_id)]
    else:
        user_like = data_base_.get_objs(['user', user_id, 'like', 'item'], key="动态")
    n_user_like = len(user_like)
    n_recently_like = 100
    threshold = 100
    n_recently_like = min(n_recently_like, n_user_like)
    clubs_list = list(dict.fromkeys(map(lambda club: club.split(":")[-1].split("_")[0],
                                        list(filter(lambda s: s.startswith("动态"), data_base_.clubs)))))[: -1]
    n_clubs = len(clubs_list)
    if n_recently_like > 0:
        recently_like = user_like[-n_recently_like:]
        user_data = np.zeros([n_recently_like, n_clubs], dtype=float)
        for i in range(n_recently_like):
            clubs_for_item = list(map(lambda s: s.split(":")[-1].split("_")[0],
                                      data_base_.get_objs(['item', recently_like[i], 'have', 'club'], key="动态")))
            for club in clubs_for_item:
                user_data[i, clubs_list.index(club)] = 1
        user_data = preprocessing.normalize(user_data, "l1")
        user_vector = user_data.sum(axis=0)/n_recently_like
    else:
        user_vector = np.array([1/n_clubs] * n_clubs)

    # 获得物品特征向量
    items_data = np.zeros([n_alpha, n_clubs], dtype=float)
    alpha = list(alpha)
    for i in range(n_alpha):
        # print("the item is " + alpha[i])
        clubs_for_item = list(map(lambda s: s.split(":")[-1].split("_")[0],
                                  data_base_.get_objs(['item', alpha[i], 'have', 'club'], key="动态")))
        for club in clubs_for_item:
            items_data[i, clubs_list.index(club)] = 1

    # item_mapper = dict(zip(alpha, list(range(n_alpha))))
    item_inv_mapper = dict(zip(list(range(n_alpha)), alpha))  # 将0～n_alpha-1反映射到召回集的物品id

    beta = _sort_items(user_vector, item_inv_mapper, items_data, n_alpha, 'cosine')
    n_beta = len(beta)

    if n_beta > threshold:
        raise ValueError(f"输出推荐集beta的长度错误，大于{threshold}")
    if not n_beta == n_alpha:
        raise ValueError(f"输出推荐集beta的长度错误，与输入集alpha的长度不等")
    # print("输出推荐集beta的长度为：{}".format(n_beta))
    return beta, n_beta


def _rearrangement(user_id: str, beta: list, n_beta: int, train_data: list, data_base_: DataBase, test_flag: bool):
    """
    人工重排算法
    :param user_id: 用户id
    :param beta: 机器排序得到的列表
    :param n_beta: 输出推荐集n_beta的元素个数
    :param train_data:所有用户点赞的训练物品集
    :param data_base_: 类数据库类的实例
    :param test_flag:是否测试
    :return: 列表gama（最终推荐集）和列表gama的元素个数
    """
    m = data_base_.get_objs(["club", "动态:二级标签:推广集", "have", "selected_item"], key="动态")

    if test_flag:
        like_items = train_data[str(user_id)]
    else:
        like_items = data_base_.get_objs(["user", str(user_id), 'like', 'item'], key="动态")
    view_items = data_base_.get_objs(['user', str(user_id), 'view', 'item'], key="动态")
    create_items = data_base_.get_objs(['user', str(user_id), 'create', 'item'], key="动态")
    m = [i for i in m  if (i not in like_items) and (i not in view_items) and (i not in create_items)]
    n_m = len(m)

    thresholds = [0, 45, 50, 45]

    if n_beta == thresholds[0]:
        gama = random.sample(m, k=min(n_m, thresholds[2]))
        n_gama = len(gama)
    elif 0 < n_beta <= thresholds[1]:
        [gama, n_gama] = _join_contents_list(m, n_m, beta, n_beta, thresholds[2])
    else:
        beta_hat = beta[: thresholds[3]]
        beta_ = beta[thresholds[3]:]
        beta1 = list(set(m) | set(beta_))
        beta1_hat = beta1[: 50 - thresholds[3]]
        gama = beta_hat + beta1_hat

    gama = list(filter(lambda s: '动态:二级标签:剧本杀' in data_base_.get_objs(['item', s, 'have', 'club'], key="动态"), gama))
    n_gama = len(gama)

    if n_gama > thresholds[2]:
        raise ValueError(f"输出推荐集gama的长度错误，大于{thresholds[2]}")
    # print("输出推荐集gama的长度为：{}".format(n_gama))
    return gama, n_gama


def run_generalized_cf(user_id, _data_base, train_data=None, test_flag=False):
    # print("用户ID: {}".format(user_id))

    alpha, n_alpha = _prefilter(user_id, train_data, _data_base, test_flag)
    # print("alpha集: 元素个数{}\n{}\n".format(n_alpha, alpha))

    beta, n_beta = _machine_sorting(user_id, alpha, n_alpha, train_data, _data_base, test_flag)
    # print("beta集: 元素个数{}\n{}\n".format(n_beta, beta))

    gama, n_gama = _rearrangement(user_id, beta, n_beta, train_data, _data_base, test_flag)
    # print("gama集: 元素个数{}\n{}\n".format(n_gama, gama))

    return _data_base.filter("动态", gama, del_prefix=False)
