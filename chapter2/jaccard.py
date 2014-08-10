# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

# jaccard係数
# 集合間類似性スコアを算出するもの
# sim(Ci, Cj) = 部分集合/全体集合
# 値の取りうる範囲は0~1
# このように展開する
# sim(Ci, Cj) = 部分集合 / (Ci + Cj - 部分集合) (全体集合を求める時間分だけ短縮される)

def sim_jaccard(prefs, p1, p2):
  # Get the list of shared_items
  subset = set(prefs[p1].keys()).intersection(prefs[p2].keys())

  # if they have no ratings in common, return 0
  s_len = len(subset)
  if s_len==0: return 0

  jaccard = float(s_len / (len(prefs[p1]) + len(prefs[p2]) - s_len))

  return jaccard
