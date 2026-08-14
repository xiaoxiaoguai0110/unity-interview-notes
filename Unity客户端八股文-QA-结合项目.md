# Unity 客户端八股文（QA 版 · 结合项目实战）

> 全篇采用一问一答形式，每题给出标准答题要点 + 示例代码，适合面试前自测与背诵。文中 🎮 标记的内容是把考点和你自己的项目（3DActGame / KitchenChaosProject）结合的例子，回答面试题时优先用自己的代码说话；每节末尾的"项目实战扩展题"是面试官大概率追问的项目问题。
> 修改/增删题目后运行 `python build_html.py Unity客户端八股文-QA-结合项目.md Unity客户端八股文-QA-结合项目.html "Unity 客户端八股文（QA 版 · 结合项目）"` 可重新生成 HTML。

## 目录

0. [项目背景](#项目背景答题素材速览)
1. [C# 基础](#1-c-基础)
2. [Unity 生命周期与脚本](#2-unity-生命周期与脚本)
3. [协程与异步](#3-协程与异步)
4. [物理系统](#4-物理系统)
5. [渲染与图形学](#5-渲染与图形学)
6. [Shader](#6-shader)
7. [UGUI](#7-ugui)
8. [资源管理与热更新](#8-资源管理与热更新)
9. [内存管理与性能优化](#9-内存管理与性能优化)
10. [动画系统](#10-动画系统)
11. [网络编程](#11-网络编程)
12. [设计模式](#12-设计模式)
13. [数据结构与算法](#13-数据结构与算法)
14. [游戏客户端架构](#14-游戏客户端架构)
15. [常用框架与工具](#15-常用框架与工具)
16. [高频面试题速查](#16-高频面试题速查)

---

## 项目背景（答题素材速览）

以下两个 Unity 项目贯穿全文。面试提到项目时，先一句话说清"项目是什么 + 你负责什么 + 技术亮点是什么"：

| 项目 | 一句话定位 | 技术亮点（都是你的面试弹药） |
|---|---|---|
| 3DActGame（类魂动作游戏） | Unity 2022.3 3D 动作游戏练习 | 五段连招（ComboStage + Animator）、敌人 FSM（Idle/Patrol/Pursuit/Attack/GetHit）、NavMeshAgent 寻路、Animation Event 做伤害判定（扇形检测 ±60°）、CharacterController 移动、事件驱动血量（Health.OnHealthChanged）、单例 AudioManager |
| KitchenChaosProject（本地双人厨房模拟） | 基于教程重构扩展的独立项目 | AI 队友系统（显式状态机）、目标选择差集算法（订单需求 - 台面已有 = 真正缺的）、配方反向追溯、按订单锁定装盘、BaseCounter 抽象基类 + 7 子类多态、ScriptableObject 数据驱动、C# event 模块解耦、双输入系统（New Input System + 直接轮询） |

> 自我介绍模板："我做了两个 Unity 项目：一个是类魂动作游戏，重点练战斗系统和敌人 AI；另一个是厨房模拟双人合作游戏，我在教程基础上独立实现了 AI 队友系统，包含决策状态机和配方推导逻辑。两个项目分别锻炼了我战斗系统设计和 AI 架构设计的能力。"

---

## 1. C# 基础

**Q1：值类型和引用类型有什么区别？请用代码说明赋值行为。**

值类型（struct/enum/基本类型）存值，赋值是拷贝；引用类型（class/string/数组/委托）存引用，赋值共享同一对象。值类型入栈/内联，引用类型对象在堆上。

```csharp
public struct Point { public int x, y; }        // 值类型
public class Player { public int hp; }           // 引用类型

Point a = new Point(); a.x = 1;
Point b = a; b.x = 2;          // b 是拷贝，a.x 仍为 1

Player p1 = new Player(); p1.hp = 100;
Player p2 = p1; p2.hp = 50;    // p2 引用同一个对象，p1.hp == 50
```

面试加分：答出"结构体默认按值传递、class 按引用传递"；性能上 struct 缓存友好但过大拷贝开销也大。

**Q2：什么是装箱拆箱？怎么避免？**

装箱是值类型转成 `object`/接口时在堆上分配并拷贝值；拆箱是反向转换，要求类型匹配。装箱会产生堆分配和 GC 压力。

```csharp
int x = 5;
object o = x;              // 装箱：堆分配
int y = (int)o;            // 拆箱：类型必须匹配

// 避免：使用泛型集合，不用非泛型集合
List<int> good = new List<int>();   // 不装箱
ArrayList bad = new ArrayList();    // bad.Add(5) 每次装箱

string s1 = x.ToString();           // ToString 不装箱
string s2 = "v=" + x;               // 拼接值类型会装箱，大量拼接用 StringBuilder
```

**Q3：为什么字符串大量拼接慢？StringBuilder 的原理？**

`string` 不可变，`+` 每次拼接都会创建新字符串，循环拼接复杂度 O(n²) 且产生大量垃圾。`StringBuilder` 内部维护可变 `char[]` 缓冲区，容量不足时翻倍扩容，只在最后 `ToString()` 分配一次。

```csharp
string s = "";
for (int i = 0; i < 10000; i++) s += i.ToString();   // 慢：每次新建字符串

var sb = new StringBuilder(64);
for (int i = 0; i < 10000; i++) sb.Append(i);         // 快：复用内部缓冲区
string result = sb.ToString();
```

**Q4：委托和事件的区别？**

委托是类型安全的函数指针，支持多播；事件是对委托的封装，外部只能 `+=`/`-=`，不能直接 `Invoke`。事件用于发布-订阅解耦，委托适合回调参数传递。

```csharp
public delegate void DamageHandler(int dmg);

public class Unit {
    public event DamageHandler OnDamaged;   // 事件：外部只能注册/注销
    public Action<int> onDeath;             // 委托字段：外部可随意调用（不推荐）

    public void DealDamage(int dmg) {
        OnDamaged?.Invoke(dmg);             // 只有本类能触发事件
    }
}

unit.OnDamaged += (d) => Debug.Log("受击 " + d);   // 订阅
unit.OnDamaged -= handler;                          // 记得反注册，防泄漏
```

> 🎮 **结合你的项目（KitchenChaos）**：你项目里的事件解耦就是用 C# `event` 做的——`OrderManager.OnRecipeSpawned` 同时被订单 UI 和 AI 决策模块订阅，新增模块不用改 OrderManager；`CuttingCounter.OnCut` 被 SoundManager 订阅播放切菜音效；`KitchenObjectHolder.OnDrop/OnPickup` 触发全局拾取/放下音效。面试话术："订单系统只负责发布事件，UI 和 AI 各自订阅互不引用，所以加新功能不需要动订单模块。"

> 🎮 **结合你的项目（3DActGame）**：血量组件 `Health` 定义 `OnHealthChanged` 事件，玩家和敌人的血条 UI 都订阅它刷新，而 Health 本身不认识任何 UI——这就是事件驱动的好处。

**Q5：泛型为什么能避免装箱？有哪些约束？**

泛型在编译期确定类型，值类型用泛型容器/方法时按原类型处理，无需转 `object`。约束用 `where` 限定类型参数。

```csharp
T Max<T>(T a, T b) where T : IComparable<T> {
    return a.CompareTo(b) >= 0 ? a : b;
}

int m = Max(3, 5);        // 值类型，不装箱
string t = Max("a", "b");

// 常用约束：where T : class / struct / new() / 基类 / 接口
T Create<T>() where T : new() => new T();
```

**Q6：深拷贝和浅拷贝怎么实现？**

浅拷贝只复制引用，深拷贝复制所有引用对象内容。类里有引用类型字段时，默认拷贝都是浅拷贝。

```csharp
public class Skill {
    public int id;
    public float[] mods;                    // 引用类型字段

    public Skill ShallowCopy() => (Skill)MemberwiseClone();   // mods 仍共享

    public Skill DeepCopy() => new Skill {
        id = id,
        mods = (float[])mods.Clone()        // 数组单独克隆一份
    };
}
```

**Q7：async/await 的原理？Unity 中使用要注意什么？**

`async/await` 由编译器生成状态机（`IAsyncStateMachine`），挂起时不阻塞线程，完成后回调继续执行。Unity 注意：`async void` 异常难捕获易崩溃；MonoBehaviour 销毁后回调仍可能执行；引擎 API 只能在主线程调用。

```csharp
async Task<int> LoadAsync() {
    await Task.Delay(100);        // 挂起 100ms，不阻塞调用线程
    return 42;
}

// 配合 UniTask 在 Unity 中更好用（自动切回主线程、可取消）
async UniTaskVoid LoadAndShow() {
    var cfg = await Resources.LoadAsync<TextAsset>("cfg");
    Show(cfg.text);
}
```

**Q8：const、readonly、静态构造函数各有什么特点？**

`const` 编译期常量，必须是字面量，编译时替换；`readonly` 运行时只读，可在构造函数中赋值；静态构造函数在首次访问静态成员时执行且只执行一次。

```csharp
public class Config {
    public const int MaxLevel = 100;                 // 编译期常量
    public static readonly string Version = "1.0.0"; // 运行时只读
    public static int LoadCount { get; private set; }

    static Config() {                                // 首次访问静态成员时执行一次
        LoadCount = LoadFromDisk();
    }
}
```

**Q9（项目实战）：你项目里怎么用事件解耦的？举一个具体例子。**

答题思路：先说事件模型（发布-订阅），再说你项目里的真实例子，最后说坑（反注册）。

```csharp
// KitchenChaos：切菜台只发布事件，音效系统订阅，两边互不认识
public class CuttingCounter : BaseCounter {
    public event EventHandler OnCut;              // 发布方不认识订阅者

    public void Cut() {
        OnCut?.Invoke(this, EventArgs.Empty);     // 切一下发一次
    }
}

public class SoundManager : MonoBehaviour {
    void Start() => FindObjectOfType<CuttingCounter>().OnCut += PlayCutSound;
    void OnDestroy() { /* 记得 -= 反注册，防止泄漏 */ }
}
```

答题要点：① 模块间只依赖事件、不互相引用；② 订阅方在 `OnDisable`/`OnDestroy` 反注册；③ 高频事件注意 GC（用 struct 事件参数或复用对象）。

**Q10（项目实战）：值类型和引用类型在你的项目里体现在哪？**

答题思路：`AIState` 枚举是值类型（switch 直接比较），`KitchenObject` 是引用类型（场景对象）。面试常追问"你代码里哪里用到了"。

```csharp
// KitchenChaos：AI 状态用枚举（值类型），按状态分发逻辑
enum AIState { Idle, MovingToTarget, Cutting, Waiting }

AIState state = AIState.Cutting;
if (state == AIState.Cutting) { /* 切菜逻辑 */ }   // 整型比较，开销小
```

> 加分点：能说出"枚举切状态本质是整型比较，比字符串比较快"，说明你懂底层。

---

## 2. Unity 生命周期与脚本

**Q1：MonoBehaviour 生命周期方法的执行顺序是什么？**

`Awake → OnEnable → Start → FixedUpdate → Update → LateUpdate → OnDisable → OnDestroy`。同一帧先执行所有 `Awake` 再执行所有 `Start`；`OnGUI` 每帧多次，避免用于游戏 UI。

```csharp
public class LifecycleDemo : MonoBehaviour {
    void Awake()      { Debug.Log("1 Awake"); }       // 创建时立即调用，无论是否启用
    void OnEnable()   { Debug.Log("2 OnEnable"); }    // 每次 SetActive(true) 调用
    void Start()      { Debug.Log("3 Start"); }       // 首帧 Update 前，只一次
    void FixedUpdate(){ Debug.Log("4 FixedUpdate"); } // 固定步长 50Hz，物理
    void Update()     { Debug.Log("5 Update"); }      // 每帧
    void LateUpdate() { Debug.Log("6 LateUpdate"); }  // Update 后，相机跟随
    void OnDisable()  { Debug.Log("7 OnDisable"); }   // SetActive(false)/enabled=false
    void OnDestroy()  { Debug.Log("8 OnDestroy"); }   // 销毁时
}
```

> 🎮 **结合你的项目（3DActGame）**：这三个回调你项目里都用到了——`Player` 的 `Awake` 缓存 `InputReader/Animator/CharacterController/Health` 组件引用；`Enemy` 的 `Awake` 缓存 `NavMeshAgent`；`CameraController` 在 `LateUpdate` 里跟随玩家，保证玩家 `Update` 移动完、`Animator` 更新完后再跟，画面不抖。面试说"相机跟随放 LateUpdate，因为要等角色和动画都更新完"就是标准答案。

**Q2：Awake 和 Start 的区别？各自适合做什么？**

`Awake` 在实例创建时同步调用（组件未启用也会执行），适合初始化自身字段、缓存组件引用、注册事件；`Start` 在第一次 `Update` 前调用（要求组件启用），适合依赖其他对象已经初始化完成的逻辑。

```csharp
public class Hero : MonoBehaviour {
    Rigidbody rb;
    Animator anim;

    void Awake() {
        rb = GetComponent<Rigidbody>();   // 缓存组件，避免每帧查找
        anim = GetComponent<Animator>();
    }

    void Start() {
        GameManager.Instance.Register(this);   // 依赖全局管理器已就绪
    }
}
```

**Q3：Update、FixedUpdate、LateUpdate 各自什么时候用？移动刚体该用哪个？**

`FixedUpdate` 固定步长，处理物理；`Update` 每帧处理输入和游戏逻辑；`LateUpdate` 在 `Update` 后执行，适合相机跟随。移动刚体用 `FixedUpdate` + `velocity`/`MovePosition`，不要直接改 `transform.position`。

```csharp
void FixedUpdate() {
    rb.velocity = new Vector3(Input.GetAxis("Horizontal") * speed, rb.velocity.y, 0);
}

void Update() {
    if (Input.GetKeyDown(KeyCode.Space)) { animator.SetTrigger("Jump"); }
}

void LateUpdate() {
    cam.transform.position = player.position + offset;   // 角色移动完再跟随，避免抖动
}
```

> 🎮 **结合你的项目（3DActGame）**：你的玩家用 `CharacterController`，所以在 `Update` 里移动（不涉及物理引擎）；敌人用 `NavMeshAgent` 也是 `Update` 驱动；相机跟随在 `LateUpdate`。面试官若问"你项目里为什么没有 FixedUpdate"，可以答："我的移动不走 Rigidbody 物理，CharacterController/NavMeshAgent 的 Move 在 Update 调用即可，物理引擎没参与。"

**Q4：如何高效地获取组件引用？**

避免每帧 `GetComponent`/`Find`/`FindObjectOfType`，在 `Awake` 缓存引用；用 `TryGetComponent` 避免异常开销；用 `[RequireComponent]` 保证组件一定存在。

```csharp
[RequireComponent(typeof(Rigidbody))]
public class Mover : MonoBehaviour {
    Rigidbody rb;

    void Awake() => rb = GetComponent<Rigidbody>();   // 缓存

    void Update() {
        if (TryGetComponent(out AudioSource src)) {  // 可选组件，安全获取
            src.Play();
        }
    }
}
```

**Q5：SetActive(false) 和 enabled=false 的区别？协程会停止吗？**

`SetActive(false)` 禁用整个 GameObject（含子物体），触发 `OnDisable`；`enabled=false` 只禁用该组件（`Update` 不再调用）。两者都不会停止协程，协程只在 `StopCoroutine`/销毁对象时停止。

```csharp
gameObject.SetActive(false);   // 整棵子树隐藏，OnDisable 触发
enabled = false;               // 只停脚本回调

IEnumerator Loop() {
    while (true) {
        Debug.Log("tick");
        yield return new WaitForSeconds(1);
    }
}
// SetActive(false) 后上面的协程仍会继续执行
```

**Q6：如何让一个对象跨场景不销毁？**

`DontDestroyOnLoad` 让对象在场景切换时保留，常用于全局管理器。注意：只能对根节点对象调用；单例注意重复实例的清理。

```csharp
public class GameRoot : MonoBehaviour {
    public static GameRoot Instance { get; private set; }

    void Awake() {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);   // 场景切换不销毁
    }
}
```

**Q7：Destroy 和 DestroyImmediate 有什么区别？**

`Destroy` 延迟到当前帧末执行，安全；`DestroyImmediate` 立即销毁，可能破坏渲染顺序或导致引用悬空，只在编辑器工具/特定场景使用。释放资源用 `Destroy`，配合对象池复用。

```csharp
Destroy(gameObject);          // 帧末销毁，推荐
DestroyImmediate(obj);        // 立即销毁，仅编辑器等特殊情况

// 对象池释放对象时更推荐直接 SetActive(false)
pool.Release(obj);
```

**Q8（项目实战）：你项目里怎么缓存组件引用、避免每帧查找？**

```csharp
// 3DActGame：Player 在 Awake 一次性缓存所有组件
public class Player : MonoBehaviour {
    InputReader input;
    Animator anim;
    CharacterController cc;
    Health health;

    void Awake() {
        input = GetComponent<InputReader>();
        anim = GetComponent<Animator>();
        cc = GetComponent<CharacterController>();
        health = GetComponent<Health>();
    }

    void Update() {
        // 直接用缓存的 input/cc，绝不 GetComponent
    }
}
```

答题要点：① `Awake` 缓存、`Update` 直接用；② 反例：每帧 `GetComponent`/`Find` 都是开销；③ 配合 `[RequireComponent]` 保证组件存在。

---

---

## 3. 协程与异步

**Q1：协程的原理是什么？**

协程是迭代器：方法返回 `IEnumerator`，Unity 每帧调用 `MoveNext()`，遇到 `yield return` 挂起，根据返回的指令决定何时恢复。协程运行在主线程，不是多线程。

```csharp
IEnumerator Demo() {
    Debug.Log("start");
    yield return null;                    // 下一帧恢复
    Debug.Log("one frame later");
    yield return new WaitForSeconds(1f);  // 等 1 秒（受 timeScale 影响）
    Debug.Log("1 second later");
    yield return new WaitForEndOfFrame(); // 本帧渲染结束后
}
```

**Q2：协程和线程有什么区别？各自适合什么场景？**

协程是单线程协作式调度，能挂起/恢复但不能并行，适合分帧处理、等待异步完成；线程是真并行，适合耗时计算，但 Unity API 大多只能在主线程调用，需注意线程安全。

```csharp
// 协程：分帧加载，避免一帧卡死
IEnumerator LoadAll() {
    for (int i = 0; i < items.Count; i += 10) {
        for (int j = i; j < i + 10 && j < items.Count; j++) {
            Process(items[j]);
        }
        yield return null;               // 每帧只处理 10 个
    }
}

// 线程：耗时计算并行执行
ThreadPool.QueueUserWorkItem(_ => {
    var result = HeavyCompute();
    // 不能直接操作 Unity 对象，需要回主线程
});
```

**Q3：如何启动和停止协程？SetActive(false) 会停止协程吗？**

用 `StartCoroutine` 启动；`StopCoroutine`/`StopAllCoroutines` 停止；销毁 GameObject 自动停止。`SetActive(false)` 和 `enabled=false` 都不会停止协程。

```csharp
IEnumerator timer = Countdown();
StartCoroutine(timer);
StopCoroutine(timer);          // 传 IEnumerator 引用停止
StopAllCoroutines();           // 停止该 MonoBehaviour 上所有协程

// 注意：字符串方式 StartCoroutine("Countdown") 停止也要用同名
```

**Q4：WaitForSeconds 每次 new 会产生 GC 吗？怎么优化？**

会。`WaitForSeconds` 是引用类型，每次 `new` 都分配堆内存。高频使用应缓存复用。

```csharp
// 差：每次生成新对象
while (true) { yield return new WaitForSeconds(1f); }

// 好：缓存复用
static readonly WaitForSeconds oneSec = new WaitForSeconds(1f);
while (true) { yield return oneSec; }
```

> 🎮 **结合你的项目（KitchenChaos）**：你调 AI 冷却时间从 0.8s 降到 0.15s 解决"频繁发呆"的问题，本质就是计时器设计问题。面试讲这个故事："AI 首次交互后有 0.8s 冷却导致频繁发呆（体验问题），缩短到 0.15s 后连贯性大幅提升。"如果再把 `WaitForSeconds` 缓存复用，还能顺带讲 GC 优化。

**Q5：如何用协程实现带进度的下载加载？**

`UnityWebRequest.SendWebRequest()` 返回异步操作，轮询 `progress` 更新进度条，完成后处理结果。

```csharp
IEnumerator Download(string url) {
    using var req = UnityWebRequest.Get(url);
    var op = req.SendWebRequest();
    while (!op.isDone) {
        progressBar.value = op.progress;
        yield return null;
    }
    if (req.result == UnityWebRequest.Result.Success) {
        byte[] data = req.downloadHandler.data;   // 使用数据
    } else {
        Debug.LogError(req.error);
    }
}
```

**Q6：协程有哪些替代方案？**

`async/await`（配合 UniTask）能完全替代协程：无 `YieldInstruction` 分配、支持取消（`CancellationToken`）、异常处理更完善、不依赖 MonoBehaviour。

```csharp
// UniTask 示例
async UniTaskVoid LoadAndShow() {
    await UniTask.Delay(TimeSpan.FromSeconds(1));
    var tex = await Addressables.LoadAssetAsync<Texture2D>("icon");
    image.sprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), Vector2.one * 0.5f);
}
```

**Q7（项目实战）：你项目里用过 Invoke 吗？它有什么坑？怎么重构？**

答题思路：诚实说"早期用过，后来发现坑就换了"，重点讲坑和重构方案（面试官想听的成长性）。

```csharp
// 3DActGame 原写法：字符串调用 + 魔法数字
Invoke("DisableDamage", 0.5f);        // 方法名拼错编译不报错，运行时才炸

// 重构：TimerManager 统一管理，可取消、可暂停、可传参
TimerManager.Instance.Schedule(0.5f, () => _damageCollider.enabled = false);
```

Invoke 的坑：① 字符串方法名无编译期检查；② 不能传参数；③ 不能单独取消（`CancelInvoke` 是全部取消）；④ 游戏暂停行为不透明。重构收益：统一入口 + 可取消 + 配合对象池复用 Timer 实例降 GC。

---

## 4. 物理系统

**Q1：碰撞和触发事件的触发条件是什么？OnCollision 和 OnTrigger 有什么区别？**

双方都要有 `Collider`，至少一方有 `Rigidbody`。勾选 `IsTrigger` 走触发事件（无物理阻挡，只做检测）；否则走碰撞事件（有物理碰撞）。`OnTriggerEnter` 是进入区域，`OnCollisionEnter` 是物理接触。

```csharp
public class HitDetect : MonoBehaviour {
    void OnCollisionEnter(Collision c) {        // 实体碰撞
        Debug.Log("撞到 " + c.collider.name);
    }

    void OnTriggerEnter(Collider other) {       // 触发区域（勾选 IsTrigger）
        Debug.Log("进入区域 " + other.name);
    }
}
```

> 🎮 **结合你的项目（3DActGame）**：你的武器伤害检测用的是 `Box Collider`（IsTrigger）+ `Rigidbody`（IsKinematic），进入触发区域时给敌人扣血。而敌人的攻击判定是另一种思路：不用碰撞体，用 Animation Event 在攻击动画关键帧触发 `OnAttackHit()`，做一次扇形检测（距离 ≤ 攻击范围 + 角度 ±60°）。两种方案各有利弊：碰撞体简单但"刀还没挥到就命中"的问题明显；事件 + 扇形检测判定时机精确，但要多写检测逻辑。

**Q2：移动刚体有哪几种方式？有什么区别？**

直接改 `transform.position` 会绕过物理引擎，破坏模拟；设 `velocity` 是物理驱动；`MovePosition` 平滑移动且参与物理，适合 `FixedUpdate` 中调用。

```csharp
void FixedUpdate() {
    // 推荐：物理驱动
    rb.velocity = new Vector3(move.x * speed, rb.velocity.y, move.y * speed);

    // 或：平滑移动（Rigidbody 无速度但有插值效果）
    rb.MovePosition(rb.position + move * speed * Time.fixedDeltaTime);

    // 不推荐：直接改 transform，会打断物理模拟
    // transform.position += move * speed * Time.deltaTime;
}
```

**Q3：如何做射线检测且避免 GC？**

高频射线用 `RaycastNonAlloc` 写入预分配数组；低频用 `Physics.Raycast`。用 `LayerMask` 过滤层级。

```csharp
RaycastHit[] hits = new RaycastHit[8];          // 预分配，避免每帧 new

void FixedUpdate() {
    int count = Physics.RaycastNonAlloc(transform.position, transform.forward, hits, 50f, enemyMask);
    for (int i = 0; i < count; i++) {
        hits[i].collider.GetComponent<Enemy>().TakeDamage(10);
    }
}

// 单次检测
if (Physics.Raycast(ray, out RaycastHit hit, 100f, layerMask)) {
    Debug.Log(hit.collider.name);
}
```

**Q4：Rigidbody 的 Interpolation 是解决什么问题的？**

物理在固定步长（默认 50Hz）更新，渲染帧率可能不同步，导致刚体运动抖动。`Interpolate`（插值）在两个物理帧之间平滑过渡，`Extrapolate`（外推）预测下一帧位置。被跟随的目标（如玩家角色）通常开启。

```csharp
rb.interpolation = RigidbodyInterpolation.Interpolate;
```

**Q5：CharacterController 和 Rigidbody 怎么选？**

`CharacterController` 自带碰撞与斜坡/台阶处理，适合人形角色，但不受物理力影响，需手动处理重力；`Rigidbody` 走完整物理模拟，适合有受力、碰撞反弹的物体（子弹、箱子、受击位移的角色）。

```csharp
// CharacterController 方案
cc.Move((moveDir * speed + Vector3.down * gravity * Time.deltaTime) * Time.deltaTime);

// Rigidbody 方案
rb.velocity = new Vector3(input.x * speed, rb.velocity.y, input.y * speed);
```

**Q6：如何配置层之间的碰撞？物理材质怎么用？**

在 Project Settings → Physics 的碰撞矩阵中配置 Layer 间的碰撞/触发关系；`PhysicMaterial` 控制摩擦与弹性。

```csharp
var mat = new PhysicMaterial {
    bounciness = 0.8f,           // 弹性：0~1
    dynamicFriction = 0.1f,      // 动摩擦
    staticFriction = 0.4f        // 静摩擦
};
GetComponent<Collider>().material = mat;
```

**Q7（项目实战）：你项目里为什么玩家用 CharacterController、武器用 Rigidbody？**

```csharp
// 玩家：人形角色，CC 自带碰撞/斜坡处理，不受物理力影响
cc.Move(moveDir * Time.deltaTime);

// 武器：只需"检测碰撞"这一件事，用 IsKinematic 刚体 + Trigger 碰撞体
// IsKinematic = 不受物理力，只参与碰撞检测
```

答题要点：CC 适合操控型角色（不会被子弹/推力带飞）；武器/特效这类"只检测不模拟"的物体用 Kinematic Rigidbody；需要受力的物体（箱子、尸体）才用动态 Rigidbody。

> 🎮 **扩展思考**：你敌人的扇形检测现在是 `OverlapSphere` + 角度过滤，面试官可能追问 GC——高频调用建议换 `OverlapSphereNonAlloc` 预分配数组。

---

---

## 5. 渲染与图形学

**Q1：什么是 Draw Call？有哪些合批方式？**

Draw Call 是 CPU 每帧向 GPU 提交的绘制命令次数，过多会卡 CPU。合批方式：静态合批（静态物体合并网格）、动态合批（小物体运行时合并，顶点数受限）、GPU Instancing（同网格同材质批量绘制）、SRP Batcher（URP/HDRP 减少状态切换）。

```csharp
// GPU Instancing：一次调用绘制大量同构物体（草、子弹、人群）
Graphics.DrawMeshInstanced(mesh, material, matrices, matrices.Length);
// 要求：相同网格 + 相同材质 + Shader 支持 instancing
```

```hlsl
// Shader 侧需要声明支持实例化
#pragma multi_compile_instancing
```

**Q2：纹理内存怎么计算？移动端用什么压缩格式？**

纹理内存 ≈ 宽 × 高 × 每像素字节。RGBA32 为 4 字节/像素；ETC2/ASTC 4x4 约 1 字节/像素；开启 Mipmap 总内存约为基准的 1.33 倍。移动端推荐 ASTC（质量好、块尺寸灵活）。

```csharp
// 1024x1024 RGBA32:     1024 * 1024 * 4 = 4 MB
// 1024x1024 ASTC 4x4:   1024 * 1024 * 1 = 1 MB
// 带 Mipmap 约再乘 1.33

Texture2D tex = new Texture2D(1024, 1024, TextureFormat.RGBA32, true); // 带 mipmap
```

**Q3：如何做 LOD 和遮挡剔除？**

LOD：距离相机远时切换低模，用 `LODGroup` 配置；遮挡剔除：烘焙遮挡数据，被完全遮挡的物体不渲染。两者都需配合相机视锥剔除。

```csharp
var lodGroup = gameObject.AddComponent<LODGroup>();
lodGroup.SetLODs(new[] {
    new LOD(0.5f,  new[] { highRenderer }),   // 距离 50% 以内用高模
    new LOD(0.2f,  new[] { midRenderer }),    // 20%~50% 用中模
    new LOD(0.05f, new[] { lowRenderer }),    // 5%~20% 用低模
});
```

**Q4：如何控制帧率和垂直同步？**

PC 上 `QualitySettings.vSyncCount` 与显示器刷新率同步；移动端关闭垂直同步，用 `Application.targetFrameRate` 限帧省电。

```csharp
Application.targetFrameRate = 60;       // 移动端限帧
QualitySettings.vSyncCount = 1;         // PC 垂直同步（0 关闭，1 开）
Screen.sleepTimeout = SleepTimeout.NeverSleep;   // 游戏常亮
```

**Q5：URP、HDRP、内置渲染管线怎么选？**

URP：轻量、跨平台、移动端友好，SRP Batcher 提升合批；HDRP：高质量物理渲染，面向 PC/主机，移动端开销大；内置管线：兼容性最好但维护中。选型看目标平台和画面需求。

```csharp
// URP 中开启/关闭后处理（Volume）
var volume = GetComponent<Volume>();
volume.profile.TryGet<Bloom>(out var bloom);
bloom.intensity.value = 1.5f;
```

**Q6（项目实战）：你的项目没怎么做渲染优化，面试官问渲染知识怎么答？**

答题思路：诚实 + 展示理解 + 给出落地计划，不要编。

> 参考答案："我的两个项目重点是玩法和 AI，渲染方面做了基础工作（URP 管线、图集、限制材质种类），但没有深入做 Shader 和性能优化。我正在给 3DActGame 补一个受击闪白 Shader 和描边效果，并计划用 Frame Debugger 分析 Draw Call。渲染原理（渲染管线、合批、纹理压缩）我在面试题里系统复习过。"

> 面试前务必至少手写一个最简单的 Unlit Shader 和 Outline Shader（见下节），这是客户端岗位最低门槛。

---

## 6. Shader

**Q1：写一个最简单的顶点/片元着色器（Unlit）。**

```hlsl
Shader "Custom/UnlitColor" {
    Properties { _Color ("Color", Color) = (1,1,1,1) }
    SubShader {
        Tags { "RenderType"="Opaque" }
        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata { float4 vertex : POSITION; };
            struct v2f { float4 pos : SV_POSITION; };

            fixed4 _Color;

            v2f vert (appdata v) {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);   // 模型空间 → 裁剪空间
                return o;
            }

            fixed4 frag (v2f i) : SV_Target {
                return _Color;
            }
            ENDCG
        }
    }
}
```

**Q2：ZWrite 和 ZTest 的作用？透明物体为什么要关 ZWrite？**

`ZTest` 控制片元通过深度测试的条件（默认 `LEqual`）；`ZWrite` 控制是否写入深度缓冲。透明物体按从远到近混合，若写深度会遮挡后面的透明物体，所以通常 `ZWrite Off`。

```hlsl
Shader "Custom/Transparent" {
    SubShader {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Pass {
            Blend SrcAlpha OneMinusSrcAlpha   // 标准 alpha 混合
            ZWrite Off                        // 透明物体不写深度
            ZTest LEqual

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            fixed4 _Color = fixed4(1,0,0,0.5);
            // ... vert/frag ...
            ENDCG
        }
    }
}
```

**Q3：如何实现描边（Outline）效果？**

把模型顶点沿法线外扩渲染黑色背面，再正常渲染正面，就形成描边。`Cull Front` 只画背面作为描边层。

```hlsl
Shader "Custom/Outline" {
    Properties { _Color ("Color", Color) = (1,1,1,1) _OutlineWidth ("Width", Range(0,0.1)) = 0.02 }
    SubShader {
        Pass {  // 描边层：背面外扩
            Cull Front
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            float _OutlineWidth;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; };
            v2f vert (appdata v) {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex + v.normal * _OutlineWidth);
                return o;
            }
            fixed4 frag (v2f i) : SV_Target { return fixed4(0,0,0,1); }
            ENDCG
        }
        Pass {  // 正常渲染
            Cull Back
            // ... 正常光照/颜色 ...
        }
    }
}
```

**Q4：法线贴图的原理？为什么要在切线空间采样？**

法线贴图把高模细节存成切线空间的法线扰动，让低模表面呈现凹凸光影。切线空间法线与表面方向无关，可平铺、可压缩（只存 XY 推导 Z），所以贴图存切线空间。

```hlsl
// 切线空间法线：采样的法线扰动
float3 normalTS = UnpackNormal(tex2D(_BumpMap, i.uv));      // xy → 法线
float3 normalWS = normalize(i.tangentWS * normalTS.x + i.bitangentWS * normalTS.y + i.normalWS * normalTS.z);
half ndotl = saturate(dot(normalWS, lightDirWS));
```

**Q5：Blinn-Phong 和 PBR 的区别？**

Blinn-Phong 用半角向量近似高光，公式简单、不守恒；PBR 基于微表面理论，用金属度/粗糙度描述材质，能量守恒、在不同光照环境下表现一致。

```hlsl
// Blinn-Phong 高光
half3 h = normalize(lightDir + viewDir);
half spec = pow(saturate(dot(normal, h)), _Gloss);

// PBR（URP 内置函数）
half3 specular = 0;
half oneMinusReflectivity = 0;
half3 diffColor = SAMPLE_METALLICSPECULAR(_BaseColor, metallic, specular, oneMinusReflectivity);
half3 brdf = BRDF1_Unity_PBS(diffColor, specular, oneMinusReflectivity, roughness, ndotl, ndotv, ...);
```

**Q6：如何做卡通（Toon）渐变光照？Shader 变体怎么管理？**

用 Ramp 纹理把漫反射映射成色阶，配合描边就是常见卡通风格。变体是关键字组合出的 Shader 版本，用 `shader_feature` 裁剪无用变体、`ShaderVariantCollection` 预编译。

```hlsl
// 卡通渐变漫反射
half ndotl = dot(normalWS, lightDirWS);
half rampV = ndotl * 0.5 + 0.5;                 // [-1,1] → [0,1]
half3 ramp = tex2D(_RampTex, half2(rampV, 0.5)).rgb;
```

```hlsl
// 变体控制：只在打包时包含用到的关键字组合
#pragma shader_feature _ ENABLE_FEATURE_A
// ShaderVariantCollection 预收集，减少构建体积和加载卡顿
```

**Q7（项目实战）：给你的 3DActGame 加一个"受击闪白"效果，怎么做？**

受击闪白 = 材质颜色向白色混合 + 短时间衰减，用 Shader 的 `_FlashAmount` 参数控制，C# 侧在受击时赋值。

```hlsl
Shader "Custom/HitFlash" {
    Properties {
        _BaseColor ("Base Color", Color) = (1,1,1,1)
        _FlashAmount ("Flash", Range(0,1)) = 0
    }
    SubShader {
        Tags { "RenderType"="Opaque" }
        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            float4 _BaseColor;
            float _FlashAmount;
            // ... 标准 vert/frag，frag 里返回：
            // return lerp(_BaseColor, float4(1,1,1,1), _FlashAmount);
            ENDCG
        }
    }
}
```

```csharp
// C# 侧：受击时把 _FlashAmount 顶到 1，再协程衰减回 0
IEnumerator Flash() {
    float t = 0f;
    while (t < 0.1f) {
        t += Time.deltaTime;
        renderer.material.SetFloat("_FlashAmount", 1f - t / 0.1f);
        yield return null;
    }
}
```

> 答题加分：能说出"用 lerp 混合到白色再衰减"、以及"闪白应该和 GetHit 动画同步触发，挂在受击事件上"。

---

---

## 7. UGUI

**Q1：Canvas 的三种渲染模式有什么区别？**

Screen Space Overlay：UI 永远在最上层，不随相机变化；Screen Space Camera：UI 渲染到指定相机，可被 3D 物体遮挡；World Space：UI 在世界空间（血条、飘字），可旋转缩放。

```csharp
// 运行时创建 Overlay Canvas
var go = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
var canvas = go.GetComponent<Canvas>();
canvas.renderMode = RenderMode.ScreenSpaceOverlay;
```

**Q2：锚点和 pivot 是什么？如何做屏幕自适应？**

锚点（Anchor）是 UI 相对父节点的参考点，pivot 是自身旋转/缩放中心。锚点设置拉伸时 UI 随父节点尺寸变化；结合 `CanvasScaler` 按参考分辨率缩放实现自适应。

```csharp
// 把 UI 锚到屏幕左上角（留 10px 边距）
RectTransform rt = GetComponent<RectTransform>();
rt.anchorMin = new Vector2(0, 1);
rt.anchorMax = new Vector2(0, 1);
rt.pivot = new Vector2(0, 1);
rt.anchoredPosition = new Vector2(10, -10);

// CanvasScaler：Scale With Screen Size，参考分辨率 1920x1080
scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
scaler.referenceResolution = new Vector2(1920, 1080);
```

**Q3：如何监听 UI 点击？事件系统是怎么工作的？**

两种方式：`Button.onClick` 或实现事件接口。事件系统由 `EventSystem` + `GraphicRaycaster` 组成：点击时对 UI 做射线检测，命中后通过 `ExecuteEvents` 派发事件并向上冒泡。

```csharp
// 方式一：Button
button.onClick.AddListener(OnClick);

// 方式二：接口
public class ClickMe : MonoBehaviour, IPointerClickHandler {
    public void OnPointerClick(PointerEventData eventData) {
        Debug.Log("clicked: " + name);
    }
}

// 不需要接收点击的图片关闭射线检测，减少开销
image.raycastTarget = false;
```

> 🎮 **结合你的项目（3DActGame）**：你的血条 UI 不是自己轮询血量，而是订阅 `Health.OnHealthChanged` 事件刷新——这正是"数据驱动 UI"的标准做法。敌人血条按距离显示（≤20m 显示）是每帧 `Update` 检测距离，面试官可能追问性能：距离检测可以降频（每 0.2s 一次）或改用触发器。

**Q4：UI 卡顿的常见原因？如何优化合批？**

原因：Canvas 重建频繁（改文本/颜色/位置/尺寸）、合批被打断、Mask 过多、Overdraw、文本过多。优化：动静分离 Canvas、相同图集元素相邻、TMP 文本、关闭无用 `RaycastTarget`、`RectMask2D` 代替 Mask、用 `CanvasGroup` 做整体隐藏/淡入淡出。

```csharp
// 动静分离：频繁变化的 UI 单独放一个 Canvas，避免整个大 Canvas 频繁重建
// 隐藏 UI 用 CanvasGroup，避免 SetActive 触发重建
canvasGroup.alpha = 0;
canvasGroup.interactable = false;
canvasGroup.blocksRaycasts = false;
```

**Q5：如何实现 UI 淡入淡出？**

用协程驱动 `CanvasGroup.alpha`（不破坏合批），比改 Image 颜色更高效。

```csharp
IEnumerator Fade(CanvasGroup cg, float target, float duration) {
    float t = 0f;
    float from = cg.alpha;
    while (t < duration) {
        t += Time.deltaTime;
        cg.alpha = Mathf.Lerp(from, target, t / duration);
        yield return null;
    }
    cg.alpha = target;
}
```

**Q6：如何做滚动列表并保证性能？**

用对象池复用 Item，只实例化可见数量的 Item；`ScrollRect` 滚动时回收不可见 Item。避免每帧创建销毁、避免列表全部实例化。

```csharp
public class ScrollList : MonoBehaviour {
    public ScrollRect scrollRect;
    public ObjectPool<Item> pool;      // 对象池
    List<Item> active = new List<Item>();

    void Refresh() {
        foreach (var it in active) pool.Release(it);
        active.Clear();
        for (int i = 0; i < visibleCount; i++) {
            var item = pool.Get();     // 复用，不 Instantiate
            item.Bind(data[i]);
            active.Add(item);
        }
    }
}
```

**Q7（项目实战）：你的两个项目里 UI 是怎么和数据联动的？**

```csharp
// 3DActGame：血条订阅血量事件，不用自己每帧查
public class PlayerHealthUI : MonoBehaviour {
    [SerializeField] Health health;
    [SerializeField] Slider slider;

    void OnEnable()  => health.OnHealthChanged += Refresh;
    void OnDisable() => health.OnHealthChanged -= Refresh;   // 反注册防泄漏

    void Refresh() => slider.value = health.GetHPRatio();
}

// KitchenChaos：订单列表订阅订单生成事件
// OrderManager.OnRecipeSpawned → OrderListUI 刷新 + AI 启动决策
```

答题要点：① UI 只订阅事件，不主动轮询；② 销毁/禁用时反注册；③ 高频刷新考虑降频或分帧。

---

## 8. 资源管理与热更新

**Q1：Resources、AssetBundle、Addressables 有什么区别？**

Resources：随包打进，不能热更，加载慢；AssetBundle：可独立打包、远程下载热更，需自己管理依赖/卸载；Addressables：基于 AssetBundle 的现代方案，自动管理引用计数、依赖和生命周期。

```csharp
// Resources：只能读内置资源
var prefab = Resources.Load<GameObject>("prefabs/hero");

// AssetBundle：可本地可远程，需管理依赖
var bundle = AssetBundle.LoadFromFile(path);
var hero = bundle.LoadAsset<GameObject>("hero");

// Addressables：异步 + 自动管理
var handle = Addressables.LoadAssetAsync<GameObject>("hero");
hero = await handle.Task;
```

**Q2：AssetBundle 如何加载依赖和卸载？**

通过 Manifest 获取依赖包列表，先加载依赖再加载本体；卸载用 `Unload(false)` 保留已加载资源（配合引用计数），`Unload(true)` 全部卸载（慎用）。

```csharp
// 1. 加载 Manifest
var manifestAB = AssetBundle.LoadFromFile(Path.Combine(dir, "AssetBundles"));
var manifest = manifestAB.LoadAsset<AssetBundleManifest>("AssetBundleManifest");

// 2. 先加载依赖
string[] deps = manifest.GetAllDependencies(bundleName);
foreach (var dep in deps) AssetBundle.LoadFromFile(Path.Combine(dir, dep));

// 3. 再加载本体
var bundle = AssetBundle.LoadFromFile(Path.Combine(dir, bundleName));
var obj = bundle.LoadAsset<GameObject>(assetName);

// 4. 卸载（按引用计数，而不是直接 Unload）
bundle.Unload(false);   // 卸载 AB 对象，保留已加载资源
```

**Q3：如何实现一个简单的引用计数资源管理器？**

每个资源记录引用数，`Retain` +1，`Release` -1，减到 0 时真正卸载。避免重复加载和泄漏。

```csharp
public class ResMgr {
    Dictionary<string, AssetEntry> cache = new Dictionary<string, AssetEntry>();

    class AssetEntry { public Object asset; public int refCount; }

    public T Load<T>(string key) where T : Object {
        if (!cache.TryGetValue(key, out var entry)) {
            entry = new AssetEntry { asset = Resources.Load<T>(key) };
            cache[key] = entry;
        }
        entry.refCount++;
        return (T)entry.asset;
    }

    public void Release(string key) {
        if (cache.TryGetValue(key, out var entry) && --entry.refCount <= 0) {
            cache.Remove(key);
            Resources.UnloadUnusedAssets();   // 实际项目中配合 AB Unload
        }
    }
}
```

**Q4：热更新方案有哪些？HybridCLR 的原理是什么？**

逻辑热更：xLua/toLua（Lua 解释执行）、ILRuntime（C# 解释执行）、HybridCLR（IL2CPP 下补充元数据 + 解释执行，性能接近 AOT）。资源热更：AssetBundle + 版本清单 + 增量下载。

```csharp
// HybridCLR：把热更 DLL 转成字节数组后加载
byte[] hotfixDll = File.ReadAllBytes(Application.persistentDataPath + "/hotfix.dll");
Assembly.Load(hotfixDll);   // 正常 Assembly.Load 即可（元数据已补充）
```

**Q5：热更新的完整流程是怎样的？**

启动 → 检查版本 → 下载版本清单 → 计算差异（增量）→ 下载新资源/代码 → 加载 AB 和热更程序集 → 进入游戏。

```csharp
async UniTask<bool> UpdateHotfix() {
    string remoteVer = await GetRemoteVersion();          // 请求服务器版本
    string localVer = PlayerPrefs.GetString("version");
    if (remoteVer == localVer) return true;

    var patch = await DownloadPatch(localVer, remoteVer); // 增量下载
    await ApplyPatch(patch);                              // 解压、覆盖本地文件
    PlayerPrefs.SetString("version", remoteVer);
    return true;
}
```

**Q6：对象池的完整实现？**

预创建/复用对象，避免频繁 `Instantiate`/`Destroy` 的创建开销和 GC 压力。注意容量上限、状态重置、隐藏时触发 `OnDisable`。

```csharp
public class ObjectPool<T> where T : Component {
    readonly Stack<T> pool = new Stack<T>();
    readonly T prefab;
    readonly Transform parent;

    public ObjectPool(T prefab, int prewarm, Transform parent) {
        this.prefab = prefab;
        this.parent = parent;
        for (int i = 0; i < prewarm; i++) {
            var obj = Create();
            obj.gameObject.SetActive(false);
            pool.Push(obj);
        }
    }

    T Create() => Object.Instantiate(prefab, parent);

    public T Get() {
        var obj = pool.Count > 0 ? pool.Pop() : Create();
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void Release(T obj) {
        obj.gameObject.SetActive(false);   // 触发 OnDisable，隐藏
        pool.Push(obj);
    }
}
```

> 🎮 **结合你的项目（3DActGame 重构计划）**：对象池不是为池而池——你的 3DActGame 里高频创建/销毁的对象是受击特效（每次攻击生成、0.5s 后关闭）；如果做敌人波次刷新，敌人本身也值得池化。池化最关键的是 `OnDespawn` 状态重置（血量回满、FSM 回 Idle、计时器取消），否则复用出来的敌人全是上一个的状态。

**Q7：如何做资源预加载？**

进入关键场景前异步预加载高频资源，避免运行中卡顿；同时卸载离开场景后不再使用的资源。

```csharp
IEnumerator Preload(string[] keys) {
    var handles = new List<AsyncOperationHandle<Object>>();
    foreach (var key in keys) {
        handles.Add(Addressables.LoadAssetAsync<Object>(key));
    }
    foreach (var h in handles) yield return h;   // 全部加载完成
}
```

**Q8（项目实战）：KitchenChaos 里 ScriptableObject 是怎么做数据驱动的？**

```csharp
// 食材属性、切菜配方、烹饪配方、订单模板全部是 ScriptableObject
[CreateAssetMenu(fileName = "Recipe", menuName = "Kitchen/Recipe")]
public class RecipeSO : ScriptableObject {
    public KitchenObjectSO input;
    public KitchenObjectSO output;
    public float cuttingProgressMax;    // 需要切几下
}

// 运行时只读引用配置，加新菜品不用改代码
public class CuttingCounter : BaseCounter {
    [SerializeField] RecipeSO recipe;   // Inspector 拖配置
}
```

答题要点：① 数据与逻辑分离，改数值不重新编译；② 多个对象共享同一份配置（引用类型天然共享）；③ 和 Excel 配置表是同一思想，面试可扩展讲"配置表 → JSON → 运行时 Dictionary"。

**Q9（项目实战）：你的 AudioManager 单例是怎么写的？有什么可以改进的？**

```csharp
// 3DActGame：单例 + ScriptableObject 管理音效引用
public class AudioManager : MonoBehaviour {
    public static AudioManager Instance;         // 单例
    [SerializeField] AudioClipRefsSO clipRefs;   // 音效配置

    void Awake() {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
    }

    public void PlayAttackSound() {
        // clipRefs.attackClip 从 SO 读取，不硬编码 Resources 路径
    }
}
```

改进点：① 单例用 `Instance` + `Awake` 查重（防重复实例）；② 音效引用走 SO 而不是 `Resources.Load`（可检查、可热更）；③ 可加音量/音效池管理。

---

---

## 9. 内存管理与性能优化

**Q1：Unity 内存泄漏的常见原因有哪些？**

事件未反注册、静态字段持有对象、协程未停止、AssetBundle 未卸载、单例持有大对象、闭包/匿名委托被长期持有。排查用 Profiler Memory 面板对比快照。

```csharp
public class Leak : MonoBehaviour {
    void OnEnable() {
        EventCenter.OnLogin += OnLogin;    // 错误：忘记反注册
    }
    void OnDisable() {
        EventCenter.OnLogin -= OnLogin;    // 正确：生命周期结束即反注册
    }
}
```

**Q2：如何降低 GC 分配？**

避免装箱、字符串拼接、每帧 `new` 临时对象、LINQ 闭包；缓存 `WaitForSeconds` 和组件引用；用 `NonAlloc` 物理查询；用对象池。用 Profiler 的 GC Alloc 列定位热点。

```csharp
void Update() {
    // 差：每帧分配
    // var str = "HP:" + hp.ToString();
    // Debug.Log(str);

    // 好：复用 StringBuilder
    sb.Clear();
    sb.Append("HP:").Append(hp);
    // 需要时才输出
}
```

**Q3：物理查询怎么避免 GC？**

`RaycastAll`/`SphereCastAll` 等会分配数组，高频使用 `NonAlloc` 版本写入预分配数组。

```csharp
// 差：每帧分配数组
RaycastHit[] all = Physics.RaycastAll(ray, 100f);

// 好：预分配复用
RaycastHit[] hits = new RaycastHit[16];
int count = Physics.RaycastNonAlloc(ray, hits, 100f);
for (int i = 0; i < count; i++) { /* ... */ }
```

**Q4：如何用 Profiler 定位性能问题？**

CPU 模块看主线程/渲染线程/脚本耗时，找热点函数；Rendering 看 Draw Call 与三角形数；Memory 看托管堆和资源内存；GC Alloc 列抓分配；真机 Profiler 验证实际帧率与内存。

```csharp
// 代码打点定位耗时
var sw = System.Diagnostics.Stopwatch.StartNew();
DoHeavy();
sw.Stop();
Debug.Log("DoHeavy: " + sw.ElapsedMilliseconds + "ms");
```

**Q5：为什么要缓存组件引用？举一个反面例子。**

`GetComponent`/`Find`/`FindObjectOfType` 有查找开销，每帧调用会浪费 CPU。在 `Awake` 缓存或通过注入/事件获取。

```csharp
public class Bad : MonoBehaviour {
    void Update() {
        GetComponent<Rigidbody>().velocity = ...;          // 差：每帧查找
        GameObject.Find("Enemy").GetComponent<Enemy>().hp; // 差：字符串查找
    }
}

public class Good : MonoBehaviour {
    Rigidbody rb;
    Enemy enemy;
    void Awake() {
        rb = GetComponent<Rigidbody>();
        enemy = GameManager.Instance.GetEnemy();           // 引用注入
    }
}
```

**Q6：如何评估和优化移动端内存？**

关注：纹理（ASTC 压缩、限制尺寸、图集）、网格（减面、LOD）、音频（压缩）、Shader 变体、托管堆。用 Memory Profiler 打快照对比"进入/离开场景"判断是否泄漏。

```csharp
// 纹理导入设置：移动端推荐
TextureImporter importer = (TextureImporter)AssetImporter.GetAtPath(path);
importer.textureCompression = TextureImporterCompression.CompressedHQ;  // ASTC
importer.maxTextureSize = 1024;
```

**Q7（项目实战）：你项目里做过哪些性能优化？举一个带数字的例子。**

答题思路：没有数字的优化是"感觉"，有数字才是"成果"。用 KitchenChaos AI 的例子（体验/逻辑层面）+ 3DActGame 重构计划（GC/架构层面）。

> 例子一（KitchenChaos）：AI 首次交互后有 0.8s 冷却，导致频繁发呆。把冷却从 0.8s 优化到 0.15s 后连贯性大幅提升；同时把散落在 Update 里的 if-else 判断收归状态机各状态内部，降低每帧判断成本。
> 例子二（3DActGame 重构计划）：把 `Invoke` 字符串计时器换成 TimerManager，受击特效改对象池，用 Profiler 记录优化前后的 GC Alloc 对比。

> 面试前把重构做完并记录真实数字，这段话就是你的"项目亮点"。

---

## 10. 动画系统

**Q1：Animator 状态机怎么用？Trigger 和 Bool 参数的区别？**

状态机管理 Idle/Walk/Run/Attack 等状态和转换条件。`Trigger` 是一次性触发（使用后自动复位），适合攻击、受击；`Bool` 是持续状态，适合接地、跑步。

```csharp
animator.SetTrigger("Attack");            // 一次性，自动复位
animator.SetBool("IsGrounded", isGrounded); // 持续状态
animator.SetFloat("Speed", speed);          // 连续值
```

> 🎮 **结合你的项目（3DActGame）**：你的玩家 Animator 参数就是这三类的典型：`Speed`（float，驱动 Blend Tree 的 Idle/Walk/Run）、`ComboStage`（int，0~5 切连招段）、`OnAttack`（Trigger，触发攻击动画）；敌人还有 `OnGetHit`（Trigger，受击）和 `AttackIndex`（float 0/0.33/0.66/1 选 4 种攻击动画）。面试直接报参数名 + 用途，说明你真的调过。

**Q2：Blend Tree 解决什么问题？如何驱动？**

Blend Tree 根据参数在多个动画之间平滑混合，避免状态切换生硬。例如根据速度混合走/跑，根据方向混合移动动画。

```csharp
// 2D 混合：横向速度 + 纵向速度
animator.SetFloat("MoveX", input.x);
animator.SetFloat("MoveY", input.y);

// 1D 混合：速度大小
animator.SetFloat("Speed", rb.velocity.magnitude);
```

**Q3：动画事件和动画曲线怎么用？**

在动画关键帧添加事件，到点时回调代码（如脚步声、技能判定）；动画曲线可把数值变化暴露给代码驱动逻辑。

```csharp
// 在动画编辑器中给关键帧添加 AnimationEvent，回调方法名要一致
void OnFootstep() {
    audioSource.PlayOneShot(stepClip);
}

// 运行时添加动画事件
var evt = new AnimationEvent { time = 0.5f, functionName = "OnHitFrame" };
clip.AddEvent(evt);
```

> 🎮 **结合你的项目（3DActGame）**：你的敌人伤害判定就是 Animation Event 的标准用法：攻击动画关键帧回调 `OnAttackHit()` 做扇形检测造成伤害；动画结束回调 `OnAttackEnd()` 切回 Pursuit 并进入冷却；受击结束回调 `OnGetHitEnd()` 回 Idle（还有 1s 计时器兜底）。面试讲"判定时机放在动画关键帧而不是代码固定延迟，这样攻击动画改了判定也跟得上"是加分答案。

**Q4：多角色场景怎么优化动画性能？**

限制 Animator 数量、设置 Culling Mode（视锥外不更新骨骼）、动画压缩、LOD 切换网格。

```csharp
// 视锥外停止更新骨骼变换，仍保留根位置
animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;

// 完全剔除（不可见且不在视锥内不更新）
// animator.cullingMode = AnimatorCullingMode.CullCompletely;
```

**Q5：Root Motion 和代码移动怎么选？**

Root Motion：位移由动画驱动，动作与位移天然一致，适合受击位移、连招；代码移动：位移由逻辑控制，适合玩家操控、网络同步。二者不要混用（关掉 `Apply Root Motion` 再代码移动）。

```csharp
// 代码移动时关闭 Root Motion
animator.applyRootMotion = false;

// 逻辑移动
transform.position += moveDir * speed * Time.deltaTime;
```

**Q6（项目实战）：你的五段连招系统是怎么设计的？有什么坑？**

```csharp
// 3DActGame：ComboStage + 排队机制
void HandleAttack() {
    if (无连招)         StartCombo(1);              // 第 1 段
    else if (不在连招中) return;                     // 忽略
    else if (有预备段数) { queued++; resetTimer; }  // 记录排队攻击
    else if (已达最大段) return;
    else 预备下一段;
}

void Update() {
    // 有预备段数且当前动画可衔接 → 提交预备段
    // 动画切回 Blend Tree → 重置连招
}
```

坑（你 README 里写过的已知问题）：连招推进时机不匹配——`PrepareComboTransition(stage+1)` 设置 Animator 条件后，Exit Time 控制的 Transition 与代码实时推进 `ComboStage` 冲突。面试这么答："我把连招状态放代码侧（ComboStage + 排队），Animator 只负责表现，两者通过参数同步；遇到 Exit Time 和代码推进不同步的问题，我通过'动画切回 Blend Tree 时重置 + 排队缓冲'解决。"

**Q7（项目实战）：Root Motion 和代码移动你项目里怎么处理的？**

3DActGame 是代码移动 + 攻击中锁定移动方向：关闭 Root Motion，用 `CharacterController.Move` 驱动位移，攻击/受击时通过状态开关锁住输入。答题要点：① 玩家操控用代码移动（响应快、可控）；② 连招/受击位移这类"动作和位移强相关"的才考虑 Root Motion；③ 两者混用会导致抖动，要明确二选一。

---

---

## 11. 网络编程

**Q1：TCP 和 UDP 怎么选？KCP 是什么？**

TCP 可靠有序，适合登录、结算等关键数据；UDP 快但不可靠，适合实时战斗。KCP 是在 UDP 之上实现确认重传的可靠传输库，延迟低，常用于帧同步战斗。

```csharp
// TCP：Socket 面向连接、流式
var client = new TcpClient();
await client.ConnectAsync(host, port);

// UDP：无连接、直接发数据报
var udp = new UdpClient();
udp.Send(data, data.Length, remoteEP);
// 可靠性由上层实现（KCP/自定义 ACK）
```

**Q2：帧同步和状态同步有什么区别？帧同步如何保证确定性？**

帧同步：只同步输入指令，各端跑相同逻辑，带宽低、回放容易；状态同步：服务器权威广播状态，客户端插值表现，开发直接、防作弊好。帧同步确定性要求：逻辑与表现分离、浮点一致（定点数）、统一随机种子、固定迭代顺序。

```csharp
// 用定点数代替 float，保证不同机器结果一致
public struct Fix {
    const long Scale = 1L << 16;   // 16.16 定点
    long raw;
    public static Fix FromFloat(float f) => new Fix { raw = (long)(f * Scale) };
    public static Fix operator +(Fix a, Fix b) => new Fix { raw = a.raw + b.raw };
    public float ToFloat() => raw / (float)Scale;
}

// 统一随机种子
System.Random rng = new System.Random(seed);   // 所有端同一 seed
```

**Q3：客户端预测和服务器回滚（Rollback）的原理？**

客户端本地立即执行输入（预测），收到服务器权威状态后，如果与本地不一致，回滚到服务器状态并重放之后的输入记录，保证最终一致。格斗/射击游戏常用。

```csharp
// 伪代码
void OnLocalInput(InputCmd cmd) {
    history.Add(cmd);
    ApplyInput(cmd);               // 本地立即预测
}

void OnServerState(GameState state) {
    localState = state;            // 用服务器权威状态覆盖
    foreach (var cmd in history) { // 重放本地输入，最终收敛一致
        ApplyInput(cmd);
    }
}
```

**Q4：TCP 粘包/拆包怎么处理？**

TCP 是字节流没有消息边界，需要自定义协议：包头（长度）+ 包体。收到数据后按长度字段解析，不足的保留在缓冲区等下一次。

```csharp
// 协议格式：4 字节长度 + 消息体
void OnData(byte[] buf, ref int offset) {
    while (offset + 4 <= buf.Length) {
        int len = BitConverter.ToInt32(buf, offset);
        if (offset + 4 + len > buf.Length) break;   // 半包，等待更多数据

        HandleMessage(buf, offset + 4, len);        // 处理一个完整包
        offset += 4 + len;
    }
}
```

**Q5：心跳和断线重连怎么设计？**

定期发心跳探测连接；超时判定断线；重连成功后服务器下发快照/补发状态恢复。移动网络还要做弱网策略（缓冲、预测）。

```csharp
IEnumerator Heartbeat() {
    var wait = new WaitForSeconds(5f);
    while (true) {
        yield return wait;
        Send(new Msg { type = MsgType.Ping, time = Time.time });
    }
}

void OnTimeout() {
    Reconnect();          // 指数退避重试
}
```

**Q6：网络序列化用什么？为什么？**

JSON 可读性好但慢、体积大；Protobuf/二进制体积小、序列化快；自定义二进制最省但维护成本高。实时战斗用 Protobuf 或自定义二进制，兼顾性能与可维护性。

```csharp
// Protobuf 序列化
var msg = new MoveMsg { x = 1.2f, y = 3.4f };
using var stream = new MemoryStream();
Serializer.Serialize(stream, msg);
byte[] data = stream.ToArray();

// 反序列化
var back = Serializer.Deserialize<MoveMsg>(new MemoryStream(data));
```

**Q7（项目实战）：你项目里没做过网络，面试官问网络知识怎么办？**

答题思路：不装懂，但把原理讲清楚 + 说明你的规划。网络是客户端高频考点，必须会"概念题"（TCP/UDP、帧同步/状态同步、粘包），项目里没实践就在 UE5 学习项目里补一个小 demo 落地。

> 参考答案："我的两个 Unity 项目都是本地单机，没涉及网络。但网络原理我系统学过：TCP 可靠有序适合登录/结算，UDP 低延迟适合战斗，KCP 在 UDP 上做可靠传输；帧同步只同步输入、确定性要求高，状态同步服务器权威、客户端插值。我计划在 UE5 学习项目里补一个多人小功能把这块落地。"

> 注意：网络是区分度很高的考点，2027 年求职前至少做一个"最小帧同步/状态同步" demo，比背概念强十倍。

---

## 12. 设计模式

**Q1：单例怎么写？有什么坑？**

常用 MonoBehaviour 单例 + `DontDestroyOnLoad`；坑：重复实例、场景销毁时序、依赖隐藏难测试。用静态 `Instance` 属性 + `Awake` 中查重。

```csharp
public class GameManager : MonoBehaviour {
    public static GameManager Instance { get; private set; }

    void Awake() {
        if (Instance != null && Instance != this) {
            Destroy(gameObject);          // 重复实例直接销毁
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```

> 🎮 **结合你的项目（3DActGame）**：你的 `AudioManager` 就是单例 + ScriptableObject 的组合。面试可以主动讲："我的 AudioManager 是单例，音效引用用 AudioClipRefsSO 配置，不用 Resources.Load 硬编码路径。" 这比只背单例定义强。

**Q2：事件中心（观察者模式）怎么实现？如何防泄漏？**

用字典维护事件名 → 回调列表；发布者发事件，订阅者反注册防泄漏。事件参数尽量复用对象或使用结构体。

```csharp
public static class EventCenter {
    static readonly Dictionary<string, Action<object>> events = new();

    public static void Add(string key, Action<object> cb) {
        if (!events.TryGetValue(key, out var list)) {
            list = null;
            events[key] = list;
        }
        events[key] += cb;
    }

    public static void Remove(string key, Action<object> cb) {
        if (events.TryGetValue(key, out var list)) events[key] -= cb;
    }

    public static void Fire(string key, object arg = null) {
        if (events.TryGetValue(key, out var list)) list?.Invoke(arg);
    }
}

// 订阅方销毁时必须 Remove，否则泄漏
void OnDestroy() => EventCenter.Remove("on_coin", OnCoin);
```

> 🎮 **结合你的项目（两个项目都有）**：事件驱动是你两个项目的共同亮点。3DActGame 的 `Health.OnHealthChanged` 驱动血条 UI；KitchenChaos 的 `OrderManager.OnRecipeSpawned` 同时驱动订单 UI 和 AI 决策。面试讲"数据/逻辑层只发事件，UI 和表现层订阅，新增模块零侵入"。

**Q3：状态模式（FSM）怎么实现？和 Animator 的关系？**

把状态行为封装成类，上下文切换状态。逻辑 FSM 管玩法规则，Animator 管表现，两者通过参数联动。

```csharp
public abstract class State {
    public abstract void Enter();
    public abstract void Update();
    public abstract void Exit();
}

public class IdleState : State {
    public override void Enter() { Debug.Log("进入待机"); }
    public override void Update() { /* 检测输入切换状态 */ }
    public override void Exit() { }
}

public class FSM {
    State current;
    public void Change(State next) {
        current?.Exit();
        current = next;
        current.Enter();
    }
    public void Tick() => current?.Update();
}
```

> 🎮 **结合你的项目（两个项目都有，重点讲）**：FSM 是你最熟的考点，两个项目两种实现：
> - 3DActGame 敌人：`Idle → Patrol → Pursuit → Attack → GetHit` 五状态，用"状态 + 触发条件"驱动（距离、冷却、动画事件）；
> - KitchenChaos AI：`enum AIState + switch` 显式状态机（Idle/MovingToTarget/Cutting/Waiting），每个状态一个 `Update*()` 方法，`ChangeState()` 统一切换；
> - KitchenChaos StoveCounter：`Idle/Frying/Burning` 灶台状态机。
> 面试重点讲：为什么从"散落的 if-else"重构到显式状态机（单文件 500+ 行、Bug 难查、状态互扰）→ 状态隔离后逻辑清晰可追溯。

**Q4：工厂模式和对象池怎么结合？**

工厂把"创建对象"集中管理，配合对象池避免重复 `Instantiate`；资源加载、配置初始化都收敛到工厂。

```csharp
public class BulletFactory {
    readonly ObjectPool<Bullet> pool;

    public BulletFactory(Bullet prefab, Transform parent) {
        pool = new ObjectPool<Bullet>(prefab, 20, parent);
    }

    public Bullet Spawn(Vector3 pos, Vector3 dir) {
        var b = pool.Get();
        b.transform.position = pos;
        b.Init(dir);          // 状态重置
        return b;
    }

    public void Recycle(Bullet b) => pool.Release(b);
}
```

**Q5：命令模式用在游戏里解决什么问题？**

把请求封装成对象，支持撤销/重做、输入回放。帧同步天然是命令流：输入即命令，记录输入序列用于回放和回滚。

```csharp
public interface ICommand { void Execute(); }

public class MoveCommand : ICommand {
    readonly Player player;
    readonly Vector3 dir;
    public MoveCommand(Player p, Vector3 d) { player = p; dir = d; }
    public void Execute() => player.Move(dir);
}

// 记录输入序列，用于回放/回滚
List<ICommand> inputHistory = new List<ICommand>();
inputHistory.Add(new MoveCommand(player, Vector3.right));
```

**Q6：观察者模式在 UI 和数据之间怎么用？**

UI 订阅数据变化事件，数据变化时自动刷新，避免 UI 主动轮询。注意 UI 销毁时反注册。

```csharp
public class CoinHUD : MonoBehaviour {
    void OnEnable()  => EventCenter.Add("coin_change", OnCoinChange);
    void OnDisable() => EventCenter.Remove("coin_change", OnCoinChange);

    void OnCoinChange(object arg) {
        text.text = "金币: " + (int)arg;
    }
}

// 数据侧
public class PlayerData {
    int coin;
    public void AddCoin(int n) {
        coin += n;
        EventCenter.Fire("coin_change", coin);   // 通知 UI
    }
}
```

**Q7（项目实战）：你的 AI 队友系统用状态机解决了什么问题？**

答题思路：讲"重构动机 → 方案 → 结果"三段式，这是你最有区分度的项目故事。

> ① 动机：AI 决策逻辑散落在 Update 的 if-else 里，单文件 500+ 行，改一个逻辑容易破坏另一个；② 方案：enum AIState + switch 显式状态机，4 个状态（Idle/MovingToTarget/Cutting/Waiting）各自封装 `Update*()` 方法，`ChangeState()` 统一管理切换；③ 结果：状态流转清晰可追溯，新增行为不影响已有状态。

**Q8（项目实战）：观察者模式在你的血条/订单 UI 里怎么用的？**

```csharp
// 3DActGame：UI 订阅血量事件，Health 完全不认识 UI
health.OnHealthChanged += Refresh;
void Refresh() => slider.value = health.GetHPRatio();

// KitchenChaos：订单 UI 订阅订单事件
orderManager.OnRecipeSpawned += RefreshList;
```

答题要点：① UI 是被动刷新不是主动轮询；② OnDisable 反注册；③ 这是"数据驱动 UI"的常见面试追问。

**Q9（项目实战）：状态模式、工厂模式、对象池怎么结合？**

扩展思考：敌人从"摆场景里"改成"波次刷新"时，配合对象池：`EnemyFactory.Spawn(类型, 位置)` 内部从池里取，`OnDespawn` 把 FSM 重置回 Idle。状态（FSM）+ 对象（池）+ 创建（工厂）三者是客户端架构常考组合。

---

---

## 13. 数据结构与算法

**Q1：手写快速排序。**

分治：选基准，把小于基准的放左边、大于的放右边，递归排序。平均 O(n log n)，不稳定。

```csharp
void QuickSort(int[] a, int l, int r) {
    if (l >= r) return;
    int p = Partition(a, l, r);
    QuickSort(a, l, p - 1);
    QuickSort(a, p + 1, r);
}

int Partition(int[] a, int l, int r) {
    int pivot = a[r];
    int i = l;
    for (int j = l; j < r; j++) {
        if (a[j] < pivot) {
            (a[i], a[j]) = (a[j], a[i]);
            i++;
        }
    }
    (a[i], a[r]) = (a[r], a[i]);
    return i;
}
```

**Q2：手写 A* 寻路的核心。**

`f = g + h`：g 是已走代价，h 是到终点的估计代价（曼哈顿/欧氏距离，需可采纳）。用优先队列按 f 取节点，直到找到终点。

```csharp
// 核心伪代码（网格寻路）
PriorityQueue<Node> open = new();      // 按 f 排序
HashSet<Node> closed = new();
open.Enqueue(start, 0);

while (open.Count > 0) {
    Node cur = open.Dequeue();
    if (cur == goal) return Reconstruct(cur);   // 回溯路径

    closed.Add(cur);
    foreach (var next in GetNeighbors(cur)) {
        if (closed.Contains(next) || !Walkable(next)) continue;
        int g = cur.g + Cost(cur, next);
        if (g < next.g) {
            next.g = g;
            next.h = Heuristic(next, goal);      // 估计代价
            next.parent = cur;
            open.Enqueue(next, next.g + next.h);
        }
    }
}
```

**Q3：环形缓冲（Ring Buffer）怎么实现？用途？**

固定容量数组 + 头尾指针，写满覆盖最旧数据；用于数据流缓冲、帧同步输入缓冲、日志等，避免频繁分配。

```csharp
public class RingBuffer<T> {
    readonly T[] buf;
    int head, tail, count;

    public RingBuffer(int capacity) { buf = new T[capacity]; }

    public void Push(T v) {
        buf[tail] = v;
        tail = (tail + 1) % buf.Length;
        if (count < buf.Length) count++;
        else head = (head + 1) % buf.Length;   // 覆盖最旧
    }

    public T Pop() {
        T v = buf[head];
        head = (head + 1) % buf.Length;
        count--;
        return v;
    }
}
```

**Q4：四叉树/八叉树解决什么问题？**

空间分区加速查询：2D 用四叉树，3D 用八叉树。视野裁剪、碰撞检测、寻路时只遍历相关区域，把 O(n) 降到 O(log n + 结果数)。

```csharp
// 简化：八叉树节点
class OctreeNode {
    Bounds bounds;
    OctreeNode[] children;
    List<Collider> objects;

    public void Insert(Collider c) {
        if (!bounds.Contains(c.bounds)) return;
        if (objects.Count < MaxItems || depth >= MaxDepth) { objects.Add(c); return; }
        // 超过容量则细分 8 个子节点再插入
    }
}

// 查询：只检查与区域相交的节点
void Query(Bounds area, List<Collider> result) { /* 递归相交节点 */ }
```

**Q5：字典和哈希表注意什么？复杂度是多少？**

哈希表平均 O(1) 查询/插入，最坏 O(n)（冲突）；注意扩容、哈希函数、键不可变。Unity 中避免每帧创建字典/用大字典做高频查找。

```csharp
// 用 int 作 key 比 string 更快
Dictionary<int, Enemy> enemyMap = new();
enemyMap[enemy.id] = enemy;

// 注意：不要每帧 new Dictionary
// 预分配容量减少扩容
var cache = new Dictionary<string, Object>(512);
```

**Q6（项目实战）：KitchenChaos 的 AI 怎么算"真正缺的食材"？**

```csharp
// 订单需要的食材 - 台子上已有的 = 真正缺的（差集思想）
List<KitchenObjectSO> missing = orderIngredients
    .Where(ing => !counterHas.Contains(ing))   // list.Contains 求差集
    .ToList();
```

答题要点：① 这是集合差集问题，数据量小 O(n·m) 无所谓；② 面试官追问"数据量大怎么办"→ 用 HashSet（O(1) 查找）；③ 能说出"先算缺什么再决定拿什么，避免随机拿食材导致死锁"说明你有工程思维。

> 加分扩展：你还做了"原料追溯"——订单要 CookedMeat 时，反向查配方链追溯到 RawMeat 再走加工流程；"按订单锁定装盘"——盘子里已有食材必须是某个订单的子集才继续装，杜绝混装死锁。这些都能当"算法在项目里怎么用"的案例讲。

---

## 14. 游戏客户端架构

**Q1：UI 框架（UIManager）怎么设计？**

界面打开/关闭、层级管理、缓存复用、加载。常用做法：UIBase 基类（生命周期 Open/Close/Refresh）+ UIManager（栈管理 + 对象池 + 资源加载）。

```csharp
public abstract class UIBase : MonoBehaviour {
    public virtual void OnOpen() { }
    public virtual void OnClose() { }
}

public class UIManager : MonoBehaviour {
    readonly Dictionary<string, UIBase> opened = new();

    public T Open<T>(string path) where T : UIBase {
        if (opened.TryGetValue(path, out var ui)) {
            ui.gameObject.SetActive(true);
            return (T)ui;
        }
        var go = Instantiate(Resources.Load<GameObject>(path), canvasRoot);
        var comp = go.GetComponent<T>();
        opened[path] = comp;
        comp.OnOpen();
        return comp;
    }

    public void Close(string path) {
        if (opened.Remove(path, out var ui)) {
            ui.OnClose();
            Destroy(ui.gameObject);        // 或放入对象池
        }
    }
}
```

**Q2：事件总线如何避免模块间网状依赖？**

模块只依赖事件总线，不互相引用。注意：事件参数用结构体/复用对象减少 GC；订阅方生命周期结束时自动反注册。

```csharp
// 定义事件参数（struct 减少 GC）
public readonly struct CoinChanged { public readonly int count; }

// 数据模块
EventBus.Publish(new CoinChanged { count = coin });

// UI 模块订阅
EventBus.Subscribe<CoinChanged>(OnCoin, this);   // this 提供自动反注册
```

**Q3：资源管理器如何设计？**

统一入口：加载（缓存 + 引用计数）、卸载、异步接口、对象池。保证同一资源只加载一次、引用归零才卸载。

```csharp
public interface IResLoader {
    T Load<T>(string key) where T : Object;
    void LoadAsync<T>(string key, Action<T> done) where T : Object;
    void Release(string key);
}

// 实现要点：Dictionary 缓存 + 引用计数 + AB/Resources 切换
// 详见 8.3 引用计数资源管理器
```

**Q4：启动流程怎么设计？**

Splash → 初始化（日志/配置/SDK）→ 检查热更 → 登录 → 加载大厅 → 异步加载战斗场景。每步有进度反馈，避免卡死。

```csharp
async UniTask Startup() {
    InitLogger();
    InitConfigTable();
    await CheckAndDownloadHotfix();     // 版本检查 + 热更
    await LoadLoginScene();             // 异步加载
    LoginManager.ShowLoginUI();
}
```

**Q5：配置表怎么加载？数据驱动有什么好处？**

Excel → 工具导出 JSON/二进制 → 运行时加载进 Dictionary。好处：数值调整不用改代码、可热更、策划可自测。

```csharp
// Excel 导出为 skill.json
// [ { "id": 1001, "name": "火球", "damage": 50, "cd": 3 }, ... ]

public class SkillConfig {
    public int id; public string name; public int damage; public float cd;
}

// 运行时加载
string json = Resources.Load<TextAsset>("config/skill").text;
var list = JsonConvert.DeserializeObject<List<SkillConfig>>(json);
var skillMap = list.ToDictionary(s => s.id);

SkillConfig GetSkill(int id) => skillMap[id];
```

**Q6（项目实战）：你的 AI 队友系统整体架构是怎样的？**

答题思路：画一张"观察-决策-执行"流程图 + 说清模块边界。

> 观察：实时扫描场景（柜台占用、台面食材、手上物品、当前订单）；决策：按"手上物品 + 订单需求"选目标（差集 + 配方追溯 + 按订单锁定）；执行：状态机驱动移动/切菜/等待。模块边界：AIPlayer 是独立组件挂在 Player 上，通过 `Player.enabled = false` 禁用真人输入，UI/音效模块通过事件解耦。

**Q7（项目实战）：你的项目配置是写死的还是数据驱动的？有什么改进空间？**

> 3DActGame 现状：攻击参数（ComboDamages、冷却、范围）很多是硬编码/Inspector 手填，README 里整理成了参数表。改进方案：把这些参数收敛成 ScriptableObject 或 JSON 配置（和 KitchenChaos 的 RecipeSO 同一套思路）。面试可以主动讲："我在 KitchenChaos 学会了数据驱动，现在把 3DActGame 的数值也往配置化迁移。"

---

## 15. 常用框架与工具

**Q1：xLua 怎么和 C# 交互？**

C# 侧创建 LuaEnv 执行 Lua；Lua 侧通过 `CS.` 访问 C# 类型；Lua 函数可注册为 C# 委托供事件/回调使用。

```lua
-- Lua 侧：访问 C# 静态/实例成员
local go = CS.UnityEngine.GameObject("Hero")
go:AddComponent(typeof(CS.HeroCtrl))
```

```csharp
// C# 侧：执行 Lua
LuaEnv luaEnv = new LuaEnv();
luaEnv.DoString("print('hello from lua')");

// Lua 函数注册为回调
luaEnv.Global.Get<Action>("OnButtonClick", cb);
button.onClick.AddListener(() => cb());
```

**Q2：UniTask 相比协程有什么优势？**

无 `YieldInstruction` 堆分配、支持取消/超时/异常、可组合、自动切回主线程。适合替代协程做异步加载、倒计时、UI 流程。

```csharp
async UniTaskVoid Demo() {
    await UniTask.Delay(TimeSpan.FromSeconds(1), cancellationToken: ct);
    await button.OnClickAsync();                       // 等待点击
    await Addressables.InstantiateAsync("enemy", parent);  // 异步加载
}
```

**Q3：Addressables 的基本用法？**

加载/实例化返回 Handle，用完要 `Release`，避免资源泄漏。可配置远程/本地、自动处理依赖。

```csharp
// 加载
var handle = Addressables.LoadAssetAsync<GameObject>("enemy");
var prefab = await handle.Task;

// 实例化并释放实例
var instHandle = Addressables.InstantiateAsync("enemy", pos, rot);
var inst = instHandle.Result;
Addressables.ReleaseInstance(instHandle);   // 销毁并释放

// 场景
await Addressables.LoadSceneAsync("Level2", LoadSceneMode.Single).Task;
```

**Q4：调优工具怎么配合使用？**

先用 Profiler 定位瓶颈（CPU/GC/内存），再用 Frame Debugger 看渲染细节（合批、Draw Call），真机 Profiler 验证。改一处测一处，不要凭感觉优化。

```csharp
// 帧率监控：持续记录，定位卡顿帧
void Update() {
    frameTime += Time.unscaledDeltaTime;
    if (frameTime >= 1f) {
        fps = (int)(frameCount / frameTime);
        Debug.Log("FPS: " + fps);
        frameTime = 0; frameCount = 0;
    }
}
```

**Q5（项目实战）：你项目的版本管理/工程实践有什么可以讲的？**

KitchenChaos 是范本：语义化版本（v1.1 ~ v1.8）、每次 commit 聚焦单一变更、commit message 规范化、SSH 部署 + GitHub Actions CI/CD。面试讲"我习惯小步提交 + 语义化版本 + 每次变更可追溯"，比"我用过 git"强太多。

**Q6（项目实战）：GitHub Actions 在你项目里做了什么？**

> 自动化构建/检查，提交后自动跑。答题要点：① 说明你理解 CI 的价值（每次提交可验证、避免"我机器上能跑"）；② 能讲清 workflow 文件结构（on/push、jobs、steps）就更稳。

---

---

## 16. 高频面试题速查

**Q1：为什么不能 new 一个 MonoBehaviour？**

MonoBehaviour 生命周期由引擎调度，必须挂载在 GameObject 上；`new` 出来的只是普通 C# 对象，不会执行生命周期方法。

```csharp
// 错误：var m = new MyBehaviour();
// 正确：
AddComponent<MyBehaviour>();
Instantiate(prefab);
```

**Q2：Awake 和 Start 的执行时机？**

Awake 在创建时立即执行（未启用也执行）；Start 在首帧 Update 前执行（要求启用）。同一帧先全部 Awake 再全部 Start。

**Q3：Update、FixedUpdate、LateUpdate 怎么用？**

FixedUpdate 固定步长处理物理；Update 处理输入与逻辑；LateUpdate 相机跟随。移动刚体放 FixedUpdate，用 velocity/MovePosition。

**Q4：协程和线程的区别？**

协程主线程协作式、可挂起不能并行；线程真并行，但 Unity API 只能在主线程调用。

**Q5：OnTriggerEnter 和 OnCollisionEnter 触发条件？**

双方 Collider + 至少一方 Rigidbody；勾选 IsTrigger 走 Trigger（无物理阻挡），否则 Collision。

**Q6：什么是 Draw Call？怎么优化？**

CPU 提交绘制命令的次数。优化：静态/动态合批、GPU Instancing、SRP Batcher、图集、LOD、剔除。

```csharp
// GPU Instancing 关键代码
Graphics.DrawMeshInstanced(mesh, mat, matrices, count);
```

**Q7：AssetBundle 怎么避免内存泄漏？**

引用计数管理 + 依赖先加载 + 归零才 Unload；`Unload(false)` 保留已加载资源，`Unload(true)` 全卸（慎用）。生产环境优先 Addressables。

**Q8：如何降低 GC？**

避免装箱、字符串拼接、每帧 new；对象池复用；缓存 WaitForSeconds/组件引用；NonAlloc 物理查询；Profiler 抓 GC Alloc。

**Q9：帧同步怎么保证确定性？**

逻辑与表现分离；浮点用定点数；统一随机种子；固定迭代顺序；输入指令序列一致。

```csharp
// 定点数：用 long 表示小数，避免 float 平台差异
long raw = (long)(value * 65536f);
```

**Q10：移动端性能瓶颈通常在哪？**

Overdraw/填充率、纹理带宽与内存、托管堆 GC、CPU 脚本、合批失败、Shader 复杂度、热更解释执行开销。用真机 Profiler 定位。

**Q11：UI 卡顿的原因与优化？**

Canvas 重建频繁、合批被打断、Mask 过多、Overdraw。优化：动静分离 Canvas、TMP、关无用 RaycastTarget、RectMask2D、CanvasGroup 淡入淡出。

**Q12：纹理内存怎么算？**

宽 × 高 × 字节/像素；RGBA32 = 4B，ASTC 4x4 ≈ 1B；Mipmap 约 ×1.33。

```csharp
// 1024x1024 RGBA32 = 4MB
```

**Q13：热更新原理？**

资源用 AssetBundle + 版本清单增量下载；逻辑用 xLua/HybridCLR/ILRuntime；启动检查版本 → 下载 → 加载新资源/代码。

**Q14：ZWrite 和 ZTest 的作用？**

ZTest 深度测试条件（默认 LEqual）；ZWrite 是否写深度。透明物体关 ZWrite、Queue=Transparent、从远到近渲染。

**Q15：如何实现对象池？**

预创建 + 复用 + 容量上限 + 状态重置；高频对象（子弹/特效/UI Item）避免 Instantiate/Destroy 开销。

```csharp
public T Get() {
    var obj = pool.Count > 0 ? pool.Pop() : Create();
    obj.gameObject.SetActive(true);
    return obj;
}
```

**Q16：Mono 和 IL2CPP 的区别？**

Mono JIT：启动快、调试好、包体小，iOS 受限；IL2CPP：IL 转 C++ 原生，性能稳、包体大、构建慢，移动端默认。

**Q17：Time.timeScale 影响什么？**

影响 deltaTime、FixedUpdate 频率、WaitForSeconds；不影响 WaitForSecondsRealtime 和 Update 本身调用。

```csharp
Time.timeScale = 0f;      // 暂停游戏（UI 用不受缩放的时间）
Time.timeScale = 1f;      // 恢复
```

**Q18：如何排查内存泄漏？**

Profiler Memory 快照对比；检查事件反注册、静态引用、协程、AB 卸载、单例持有。

```csharp
void OnDisable() => EventCenter.Remove("key", handler);   // 记得反注册
```

**Q19：客户端如何做网络同步的平滑表现？**

状态同步用插值（快照间线性插值）+ 客户端预测；帧同步用延迟缓冲对齐输入。

```csharp
transform.position = Vector3.Lerp(from, to, (time - t0) / dt);
```

**Q20：如何设计技能系统？**

配置驱动 + 状态机/行为树：技能配置表（伤害/范围/CD）+ 技能流程状态 + 事件回调（命中检测、特效、音效）。

```csharp
// 配置驱动：同一套代码，不同配置 = 不同技能
var cfg = skillMap[skillId];
StartCoroutine(CastSkill(cfg.castTime, cfg.damage, cfg.range));
```

**Q21（项目向速查）：面试官问"你项目最大的难点"怎么答？**

从下面三个里选一个，讲"现象 → 定位 → 方案 → 结果"：

| 难点 | 现象 | 定位 | 方案 | 结果 |
|---|---|---|---|---|
| AI 死锁 | AI 和玩家抢同一柜台卡死 | 目标选择没考虑占用 | 每帧检测 `IsTargetCounterBlocked` + 提前换目标 | 卡死消失 |
| AI 发呆 | 交互后发呆 0.8s | 冷却过长 | 0.8s → 0.15s | 连贯性大幅提升 |
| 连招不同步 | 连招推进和动画 Exit Time 冲突 | 代码状态与 Animator 状态不同步 | 排队缓冲 + 切回 Blend Tree 重置 | 连招稳定 |

**Q22（项目向速查）：你两个项目分别展示了你什么能力？**

> 3DActGame → 战斗系统设计：连招、AI FSM、动画事件、事件驱动、性能重构（对象池 + TimerManager）。KitchenChaos → AI 与架构：状态机、差集算法、数据驱动、事件解耦、版本管理。一句话收尾："一个证明我会做战斗玩法，一个证明我能设计 AI 和架构。"
