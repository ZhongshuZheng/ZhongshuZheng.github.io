# 控制理论

*创建时间：2023-08-23*

## PID 控制

<div class="grid cards" markdown>

-   **P：比例控制**

    ---

    对“当前”预算偏差进行控制：

    $$
    a=a_0-Ke_t=a_0+K(B_{\mathrm{target}}-B_{\mathrm{actual}})
    $$

    其中，$e$ 代表预算差距。P control 没有记忆，只看当前时刻的预算差了多少。

-   **I：积分控制**

    ---

    对“历史”累计预算偏差进行控制：

    $$
    a=a_0+K\sum e
    $$

-   **D：微分控制**

    ---

    根据偏差的变化趋势进行控制：

    $$
    a=a_0+K(e_t-e_{t-1})
    $$

    这个偏差受波动影响较大，对噪声敏感，因此不常用。

</div>

## Dual Pace Control

1. 计算每时段预算：

    $$
    B_{\mathrm{target},t}=\frac{B_{\mathrm{total}}}{T}
    $$

2. 利用拉格朗日对偶转化的优化目标调整 $\lambda$ 参数。标准形式为：

    $$
    \lambda=\lambda-Ke=\lambda_0+K\sum e
    $$

    这与 I control 基本等价。通常会加入 P，来避免突然陷入高峰阶段、大量花钱而难以控制预算的情况。所以标准做法是 PI 控制的 dual variable control。

3. 面对变化的供需场景，不能使用时段均匀的预算划分，可采用“分时段预估 predictor + 分时段规划 planner + 预算控制 control”。
