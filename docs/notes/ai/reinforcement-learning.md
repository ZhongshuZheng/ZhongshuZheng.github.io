# Reinforcement Learning

*创建时间：2019-01-06*

*更新时间：2026-03-01*

在强化学习语境下，机器的行为和学习是交替进行的。

观察状态state、根据当前行动策略policy，执行行动action，查看收益reward。

## 1 马尔科夫决策过程

如果行动后获得的即时收益r与环境变化δ仅取决于当前状态，成为马尔科夫性。

状态转移模型

<figure markdown="span">
  ![状态转移模型](reinforcement-learning/images/image-01.png){ loading=lazy }
  <figcaption>状态转移模型</figcaption>
</figure>

收益函数

<figure markdown="span">
  ![收益函数](reinforcement-learning/images/image-02.png){ loading=lazy }
  <figcaption>收益函数</figcaption>
</figure>

策略函数

<figure markdown="span">
  ![策略函数](reinforcement-learning/images/image-03.png){ loading=lazy }
  <figcaption>策略函数</figcaption>
</figure>

学习目标：策略评估函数

<figure markdown="span">
  ![状态价值函数](reinforcement-learning/images/image-04.png){ loading=lazy }
  <figcaption>状态价值函数</figcaption>
</figure>

γ是折扣系数

由于V数值很多场合难以计算，计算Q数值代替

<figure markdown="span">
  ![动作价值函数](reinforcement-learning/images/image-05.png){ loading=lazy }
  <figcaption>动作价值函数</figcaption>
</figure>

Q数值和当前状态与动作相关，表示S状态下采取行动a后，在接下来均采取最优策略所获得的累计收益。新优化目标如下：

<figure markdown="span">
  ![最优策略](reinforcement-learning/images/image-06.png){ loading=lazy }
  <figcaption>最优策略</figcaption>
</figure>

### 1.1 V值策略迭代算法

根据初始状态与策略更新V值，然后更新策略，迭代更新V值。

### 1.2 Q学习算法

核心思想是，观察当前环境，更新前一状态的Q值，根据当前的Q值决策。

<figure markdown="span">
  ![Q-learning 更新公式](reinforcement-learning/images/image-07.png){ loading=lazy }
  <figcaption>Q-learning 更新公式</figcaption>
</figure>

与V值算法相比，这是模型无关的，无需记忆并更新环境模型。但效率太低。

### 1.3 Off-policy 评估方法

可以用在所有的反事实评估中。

1) Direct Method Estimator(DM)：直接使用统计数据来加权评估

2) Inverse Propensity Scoring(IPS)：IS思想，Yi \* π(A|X) / Pi

3) Doubly Robust(DR)：预估结果 + π(A|X) / Pi \* （Yi - 预估结果）

其中π是目标分布，如果是全空间内那就是1。如此预估概率与预估结果有一个准就可以

IS期望无偏推导：

希望求的期望 E\_π\[ r \] = \\sum π(a|x) \* r(s,a) = \\sum  π(a|x) / Pi \* Pi \* r(s,a)

根据期望定义，可换得 = E\_pi\[ π(A|X) / Pi \* r \]

### 1.4 On-policy 与 Off-policy

on-policy   数据是策略自己产生的，更新策略后完全不能用旧数据，各种policy based算法

off-policy   数据是探索策略产生的，两者可以有一定代差，逐渐逼近一个固定的目标，q-value算法

### 1.5 Q-based

- 核心学习内容：Q(s\_t,a) → Q(s\_t+1,a\_t+1best)+r
- dqn，d3qn：直接估计Q，选择最好的a
- ddpg：连续行为无法枚举最好，使用一个Actor出“最佳”行为，一个Critic估计Q，然后使用两对网络避免移动靶问题。两组模型，学Q的时候用第二组Target模型出“下一步的”Q'，结合真实单步reward教第一组（就是Critic的单步TD），学A的时候用自己的Q
- Td3：给ddpg每个critical加一组q，然后取小者，降低自举
- sac：与td3基本一样，就是学习目标加了个熵，增强行为探索能力
- Qbased的模型通常需要2组模型，避免自举（每次学习目标都是argmax导致）

### 1.6 Policy Gradient

- 优势估计 A(a,s)=Q(a,s)-V(s)，Q代表s下a状态后全局得分，V代表s下全局得分
    - MC方法：偏差小方差大，训练不稳定，成本高
    - 单步TD：A=r+V(s+1)-V(s) 方差小偏差大，依赖V准
        - 其原理来源于bellman bootstrap，如果目标收敛，可以满足用下一步的预估值当做未来收益的一部分
- 核心学习内容：V(s)→Q(s,π(s))=A+V(s)=TD: r+V(s+1)=GAE+V(s)
- ac，a3c：一个当做π，一个估计v，v用单步TD来学习。A3c用来多线程

#### PPO

- 核心记忆点：Actor网络是一套策略分布生成器，Critic是评估Actor在某状态下的打分，本状态打分通过下一状态Base值+真实行为Reward来逼近学习
- 核心逻辑：
    - policy gradient: loss\_PG = -E( log π(a|s)  \*  (Q(a|s) - V(s)) )，后文用A指代优势收益(Q(a|s) - V(s))，**这里 V 使用采样时 Critic 的旧预测快照，避免学习目标一直变动**
        - Q(a|s) ~= V(s+1) + reward，这是1阶TD-advantage的思路实现，GAE会更加精细，在采集数据阶段计算“链路完整”的Reward
    - IS: r = e(log π(a|s) - logπ\_old(a|s))，等价于两者相比，但这种实现能够避免概率数值过小导致下溢。这个是通过数学推导，求新行为在旧行分布上的期望值转化的
    - PPO的标准loss：loss\_PPO = - E(r \* A)
    - 裁剪化：loss\_clip = -E(min(-loss\_PPO, clip(r, 0.8, 1.2) \* A))，这个min的作用其实与if等价
    - Critic的学习目标：V(s) → A + V\_old(s)
    - GAE：相当于“多步TD”综合考虑方差与偏差，使用加权递推估计，λ=0时相当于1阶TD，λ=1时近似蒙特卡洛减去baselline，一般使用0.95左右。γ用来控制长期信息的影响力度

<figure markdown="span">
  ![GAE 计算公式](reinforcement-learning/images/image-08.jpg){ loading=lazy }
  <figcaption>GAE 计算公式</figcaption>
</figure>

- 其他工程细节：
    - PPO会给Actor加一个策略熵H(π( · |s))避免收敛过快
    - 会对Advantage使用均值与方差归一化来稳定梯度尺度，防止梯度异常把模型搞坏
    - 超参数可以直接套用StableBaseline(如SB3)
- 一般来说，PPO比DDPG更稳定，因为Actor自举与bootstrapping——没有多层TD来规范化结果、并且off-policy，每次学习的都是Q(s) = r+Q(s+1)，误差传递，并且actor学让Q最大对行为，越学误差，误差越大actor越学。不过TD3和SAC其实也在做优化。
    - 也称死亡三角，bootstrap的单步TD，加上offpolicy（，以及广泛存在的函数拟合），导致策略外推，训练错误

<figure markdown="span">
  ![PPO、DDPG、TD3 与 SAC 对比](reinforcement-learning/images/image-09.jpg){ loading=lazy }
  <figcaption>PPO、DDPG、TD3 与 SAC 对比</figcaption>
</figure>

- 在一些action训练不稳定情况下，critical网络要比action更新慢一些，避免action跟不上
    - Ddpg通常两者同步更新
- Offline-rl
    - 模仿学习：直接学习专家行为
    - Bandit：
        - Multi-arm bandit，无状态，仅讨论行为与收益，如thompson采样等方法
        - Contextual bandit：单步RL
    - 核心难点在于ood，给没见过的行为过高分
        - 有一些经典方法，通过降低没见过行为的选择或得分来控制
## 2 LLM 强化学习与 RLHF

### 2.1 经典流程

SFT → Reward Model → PPO

- SFT用固定的语料训练
- 通过人工标注的回答偏好对训练Reward Model

### 2.2 PPO

- 结构：4个网络 actor、critic、reference（old actor）、reward
- reference就是sft后的llm，用于计算KL约束
- 与传统PPO不同，有一个独立的reward网络，用来给出完整行为序列最终的reward
- Critic的训练目标依然是A+V\_old(s)

### 2.3 DPO

- 流程改为 SFT → DPO
- 使用已经收集的 prompt、preferred response 与 rejected response；结合冻结的 reference model，让模型相对于 reference 提高 preferred response 对 rejected response 的概率优势
- 不再显式训练 Reward Model，也不需要 PPO rollout 和 Critic

### 2.4 GRPO

用一组回答的均值替代掉critic。

### 2.5 GSPO

在grpo基础上，不再是每个token更新一次，而是整条链路结束后统一更新。

### 2.6 为什么没有用 SAC 之类

因为要控制不能跑太远。

参考链接：https://zhuanlan.zhihu.com/c\_1215667894253830144
