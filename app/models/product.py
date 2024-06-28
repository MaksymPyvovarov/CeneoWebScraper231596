import json
import pandas as pd
import os
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
import numpy as np

class Product:
  def __init__(self, product_id, product_name, opinions):
    self.product_id = product_id
    self.product_name = product_name
    self.opinions = opinions

  def create_charts(self):
    all_opinions = list(map(lambda opinion: opinion.convert_to_dict(), self.opinions))
    opinions = pd.DataFrame.from_dict(all_opinions)
    MAX_SCORE = 5
    opinions.score = opinions.score.apply(lambda v: round(v * MAX_SCORE, 1))
    opinions_count = opinions.index.size
    pros_count = opinions.pros.apply(lambda p: None if not p else p).count()
    cons_count = opinions.cons.apply(lambda c: None if not c else c).count()
    average_score = round(opinions.score.mean(), 2)
    score_distribution = opinions.score.value_counts().reindex(np.arange(0,5.5,0.5), fill_value = 0)
    recommendation_distribution = opinions.recommendation.value_counts(dropna=False).reindex([True, False, np.nan], fill_value = 0)
    product = {
      'product_id': self.product_id,
      'product_name': self.product_name,
      'opinions_count': int(opinions_count),
      'pros_count': int(pros_count),
      'cons_count': int(cons_count),
      'average_score': average_score,
      'score_distribution': score_distribution.to_dict(),
      'recommendation_distribution': recommendation_distribution.to_dict()
    }
    if not os.path.exists("app/products"):
      os.mkdir("app/products")
    jf = open(f"app/products/{self.product_id}.json", "w", encoding="UTF-8")
    json.dump(product, jf, indent=4, ensure_ascii=False)
    jf.close()
    matplotlib.use('Agg')
    if not os.path.exists("app/static"):
      os.mkdir("app/static")
    if not os.path.exists("app/static/charts"):
      os.mkdir("app/static/charts") 
    fig, ax = plt.subplots()
    score_distribution.plot.bar(color="turquoise", ax=ax)
    plt.xlabel("Number of stars")
    plt.ylabel("Number of opinions")
    plt.title(f"Score histogram for {self.product_name} product")
    plt.xticks(rotation=0)
    ax.bar_label(ax.containers[0], label_type='edge', fmt=lambda l: f'{int(l)}' if l else '')
    plt.savefig(f"app/static/charts/{self.product_id}_score.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    recommendation_distribution.plot.pie(
        labels=["Recommend", "Not recommend", "Indifferent"],
        label='',
        colors=["forestgreen", "crimson", "silver"],
        autopct=lambda p: f'{p:.1f}%' if p > 0 else ''
    )
    plt.title(f"Recommendation shares for {self.product_id} product")
    plt.savefig(f"app/static/charts/{self.product_id}_recommendation.png")
    plt.close(fig)