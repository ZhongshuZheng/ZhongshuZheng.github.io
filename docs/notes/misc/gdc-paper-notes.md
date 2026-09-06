# GDC 论文阅读

*创建时间：2023-01-10*

## 随机数

需要预处理尽量避免出现让人觉得“不随机”的情况发生，比如减少小概率事件。

[参考资料](http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter03_Advanced_Randomness_Techniques_for_Game_AI.pdf)

## 行为模型简介

- **层级有限状态机**：一个一个状态转移
- **行为决策树**：缺点是后期可能过于庞大
- **效用系统 utility system**：根据计算得分行动
- **面向目标的行为计划 GOAP**：设计达到目标的行为栈，需要行为标签提前标注好
- **层级任务网 HTN**：从当前状态开始，设计到目标的行为网络，以达到最终行为，类似 GOAP

[参考资料](http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter04_Behavior_Selection_Algorithms.pdf)

## 回合策略降低敌人 Turn 的 Downtime

在保障 tactic clarity 的基础上，尽量聚合 AI 行为同时进行，比如同屏幕内的共同方向移动，一时间内只有一个玩家角色被攻击。战争机器战略版设计了类似的机制，以及类似 goal 的行为队列，来实现 AI 完成不同的协同目标。

[参考资料](http://www.gameaipro.com/GameAIProOnlineEdition2021/GameAIProOnlineEdition2021_Chapter03_Gearing_the_Tactics_Genre_Simultaneous_AI_Actions_in_Gears_Tactics.pdf)

## AI 反应设计

核心就是维持玩家的 suspension of disbelieved：反馈要详略得当，越细致特殊的反馈越不应该重复，common 的反馈可以重复；群组反馈要不能完全一样，不要同时；反馈要有持续连贯性；状态机转移时需要明确反馈；AI 对玩家位置的预期正确与否带来的不同“惊讶”反馈。

[参考资料](http://www.gameaipro.com/GameAIProOnlineEdition2021/GameAIProOnlineEdition2021_Chapter11_You_had_me_at_AAAAHHH_On_the_importance_of_reactions_in_game_AI.pdf)

## 开放世界的小队 AI 合作

设计小队活动范围，互相距离不会太远；confidence 机制，决策小队队员行为；前线机制，确定前后，理清战线，避免玩家看不懂 AI 在干啥，士气不同的 AI 小队会选择轮流撤退或侧面包抄；介绍了各种场合下如何维持前线的规则与技巧。

[参考资料](http://www.gameaipro.com/GameAIProOnlineEdition2021/GameAIProOnlineEdition2021_Chapter12_Squad_Coordination_in_Days_Gone.pdf)

## 通过遗传算法组合优化来自动化测试游戏平衡性

经典遗传算法，设计模拟战斗，设计不同的得分目标，做基因优化，找到过强或弱的组合。

[参考资料](http://www.gameaipro.com/GameAIProOnlineEdition2021/GameAIProOnlineEdition2021_Chapter17_Game_Balancing_using_Genetic_Algorithms_to_Generate_Player_Agents.pdf)

## 大语言模型指导 NPC

挺牛逼的，把 GPT 当一个建议（人类）大脑，什么事情都问问他。主要实现了一个记忆力系统，每件事都记下来，标记时间与重要性，每次访问 GPT 会选取价值高的一些信息（取决于时间，重要性，和与当下场景问题的文本特征的余弦相似度）；定期进行“反思”，把自己的记忆给 GPT 看，问可以提炼哪些深层信息，然后写成新的记忆；定期根据记忆问 GPT 给出一段时间的计划，写进记忆；遇到事情根据记忆问 GPT 是否该反应，如何反应。

[参考资料](https://arxiv.org/pdf/2304.03442.pdf)

## 随机游走的分布替代

对于一些随机产生的值，如果两次产生的值间隔时间较长，比如 3 天前的价格和今天的价格，为了保障数值变化合理，需要在使其符合分布，以初始值为均值，设计方差时间间隔加权的，来采样。给出了很多场景下的公式，公式本身不太好理解，包括给定起终点的分布采样，固定形状走势的分布采样等。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter02_Creating_the_Past_Present_and_Future_with_Random_Walks.pdf)

## AI 盟友行为决策架构

龙腾世纪系列的盟友 AI 设计介绍，读着很快乐。基于 utility 系统设计，通过一种绑定“技能，用途，得分树，行为树”为一个 snippets 的方式，来实现行为决策的定制化。每个行为会根据其执行意义，被提前设计好自己的得分树和行为树，这些树可复用。AI 会遍历所有自己可用的 snippets，每个 snippets 遍历所有可用行为目标，选出最大得分者，然后选出最大得分的 snippets，按照其行为树执行。实现上估计体验会很好。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter31_Behavior_Decision_System_Dragon_Age_Inquisition’s_Utility_Scoring_Architecture.pdf)

## 效用论 Utility Theory

**得分计算：** 通过计算行为得分并正则化，给 AI 选择合适的行为。得分曲线可以选择线性，二次，logistics 以及分段线性函数（避免不该发生的事情得分）等。

**行为选择：** 通过随机加权采样或选取 top n 来增强行为的随机性；通过分桶来决策高优先层。

**惰性：** 通过冷却时间，给执行中任务加权，完成后再做新计划等方法，避免 AI 反复横跳做不完事情。给了一个 demo。

[参考资料](http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf)

## 战略图上决策 AI 应该去哪里

以 epicgame 的 paragon 为例，分析 MOBA 游戏 AI 自顶向下的指挥问题。设计一个关键点图，AI 指挥官会在关键点图上不断给出目标点以及重要性得分，逐一给目标点配置成员，配置方法根据成员-目标打分，选人去。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter24_Being_Where_It_Counts_Telling_Paragon_Bots_Where_to_Go.pdf)

## AI 健壮性测试

对 AI 的行为进行各种边界/并发测试，检查是否符合预期。包括感知，瞄准，攻击，反应等等，没细看。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter07_How_to_Build_Robust_AI_for_Your_Game.pdf)

## 兰彻斯特战争损耗模型

通过战争损耗模型预估战斗结果或战力对比。

算法公式：

`(A0^n - A^n) / b威力 = (B0^n - B^n) / a威力`

- 威力可以通过组内单位的 health × power 的均值之类计算
- n 是战争危险系数，越大杀人越快，一般取 2
- 战斗力参数可以根据经验或者历史数据回归

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter25_Combat_Outcome_Prediction_for_Real-Time_Strategy_Games.pdf)

## 时间与空间在塔防游戏 AI 计算上的应用

最简单的是空间覆盖面，然后复杂化，通过减速等方式，计算时间上的覆盖面。没太细看。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter27_The_Role_of_Time_in_Spatio-Temporal_Reasoning.pdf)

## Astar 静态图加速优化

提前把图（格子图或导航图）所有的点的每条可行边记录一个表，这个表会记下（大致记录，通过正方形凸包记录，节约空间）从这个方向走最好的终点们，runtime 时候每次只走有有记录的那些方向；这个表通过对所有点进行 floodfill 的 Dijkstra 提前计算产生（可多线程处理所有点）。

[参考资料](http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter22_Faster_A_Star_with_Goal_Bounding.pdf)

注：JPS+ 跳点搜索是目前最好的寻路算法之一，一般优于 Astar。
