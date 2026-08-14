# Unity 客户端八股文（QA 版）

> 全篇采用一问一答形式，每题给出标准答题要点 + 示例代码，适合面试前自测与背诵。修改/增删题目后运行 `python build_html.py Unity客户端八股文-QA.md Unity客户端八股文-QA.html` 可重新生成 HTML。

## 目录

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



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q2：什么是装箱拆箱？怎么避免？**

装箱（Boxing）是把值类型转换为 `object` 或接口类型：运行时会在堆上创建一个对象，把值复制进去。拆箱（Unboxing）是把这个对象取回原来的值类型，必须显式转换，而且类型必须完全匹配。装箱会产生堆分配和 GC 压力，拆箱还会产生类型检查和数据拷贝。

```csharp
int x = 5;
object o = x;              // 装箱：创建对象并复制 x
int y = (int)o;            // 拆箱：取回 int

object value = 5;
// long n = (long)value;   // 错误：value 中装箱的是 int，不是 long
long n = (long)(int)value; // 先拆成 int，再转成 long

// 避免：使用泛型集合，不用非泛型集合
List<int> good = new List<int>();   // 不装箱
ArrayList bad = new ArrayList();    // bad.Add(5) 每次装箱

string s1 = x.ToString();            // 常见情况下不需要额外装箱
string s2 = "v=" + x;               // 频繁拼接会产生临时字符串
```

面试时可以补充：`enabled = false`、`SetActive(false)` 与装箱无关；装箱主要出现在 `object`、非泛型集合、接口调用、旧式 API 或把值类型当作委托参数使用的场景。高频代码中优先使用泛型集合、泛型方法和预分配容器。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q3：为什么字符串大量拼接慢？StringBuilder 的原理？**

`string` 是不可变（immutable）引用类型。使用 `+`、`Concat` 或插值改变内容时，实际上会创建新的字符串对象，旧字符串成为垃圾。循环拼接会反复复制已有内容，通常有 O(n²) 的拷贝成本并产生大量 GC。

`StringBuilder` 内部维护可变缓冲区，`Append` 时优先写入已有容量，容量不足才扩容，最后调用 `ToString()` 生成结果。单次、少量拼接使用插值或 `string.Format` 即可；循环、大量片段拼接才适合 `StringBuilder`。

```csharp
// 反例：每次 += 都可能创建新字符串
string s = "";
for (int i = 0; i < 10000; i++)
    s += i.ToString();

// 正例：复用缓冲区
var sb = new StringBuilder(64);
for (int i = 0; i < 10000; i++)
    sb.Append(i);
string result = sb.ToString();
```

Unity 中不要在 `Update` 里反复创建临时字符串用于日志或 UI；可以降低日志频率、缓存不变文本，并复用 `StringBuilder`。注意 `StringBuilder.ToString()` 仍然会创建最终字符串，只是把分配集中到最后。



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
**Q4：委托和事件的区别？**

委托是类型安全的方法引用，可以保存一个或多个方法；事件是对委托的封装，外部只能 `+=`/`-=`，不能赋值、清空或直接 `Invoke`。事件适合发布-订阅，委托适合回调参数传递。

```csharp
public class Unit {
    public event Action<int> OnDamaged;

    public void DealDamage(int dmg) {
        // 只有 Unit 内部能触发事件
        OnDamaged?.Invoke(dmg);
    }
}

public class DamageUI {
    private Unit unit;

    public DamageUI(Unit unit) {
        this.unit = unit;
        unit.OnDamaged += ShowDamage;       // 订阅
    }

    public void Dispose() {
        unit.OnDamaged -= ShowDamage;       // 反注册
    }

    private void ShowDamage(int dmg) {
        Debug.Log("受击 " + dmg);
    }
}

// unit.OnDamaged?.Invoke(10); // 编译错误：外部没有触发权
```

Unity 中常在 `OnEnable` 订阅、`OnDisable` 反注册。不要用两个内容相同但实例不同的匿名 Lambda 进行反注册；应该保存委托引用，或使用普通方法。事件不等于“自动解除引用”，生命周期结束时仍然要取消订阅。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q5：泛型为什么能避免装箱？有哪些约束？**

泛型把类型作为参数，在编译期保留具体类型。值类型放入 `List<int>` 或传给泛型方法时，不需要先转成 `object`，因此可以避免非泛型集合常见的装箱拆箱，同时提供编译期类型检查。约束用 `where` 限定类型参数。

```csharp
T Max<T>(T a, T b) where T : IComparable<T> {
    return a.CompareTo(b) >= 0 ? a : b;
}

int m = Max(3, 5);        // 值类型，不装箱
string t = Max("a", "b");

// 常用约束：class / struct / new() / 基类 / 接口
T Create<T>() where T : new() => new T();

public class ComponentPool<T> where T : MonoBehaviour {
    private List<T> items = new List<T>();
}
```

常见误区：泛型不代表一定没有任何 GC；如果把 `T` 再转成 `object`、使用闭包或创建临时对象，仍然可能分配。泛型的核心收益是类型安全、代码复用，以及在值类型场景下避免不必要的装箱。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q6：深拷贝和浅拷贝怎么实现？**

浅拷贝只复制最外层对象；字段如果是引用类型，复制后仍指向同一个内部对象。深拷贝则要把内部引用对象也重新创建一份。类里有数组、List 或其他 class 字段时，直接赋值和 `MemberwiseClone` 都不能自动完成深拷贝。

```csharp
public class Skill {
    public int id;
    public float[] mods;

    public Skill ShallowCopy() => (Skill)MemberwiseClone();   // mods 仍共享

    public Skill DeepCopy() => new Skill {
        id = id,
        mods = (float[])mods.Clone()        // 内部数组也复制
    };
}

Skill a = new Skill { id = 1, mods = new[] { 1f, 2f } };
Skill b = a.ShallowCopy();
b.mods[0] = 99f;
// a.mods[0] == 99：浅拷贝共享同一个数组

Skill c = a.DeepCopy();
c.mods[0] = 50f;
// a.mods[0] 不会因为 c 的修改而改变
```

Unity 中 `GameObject clone = original` 只是复制引用，两个变量仍指向同一个对象；`Instantiate(original)` 才是创建一个新的 Unity 对象层级。项目中要根据需求选择复制配置数据、运行时状态还是整个对象层级，避免误把共享引用当成独立副本。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q7：数组和 `List<T>` 有什么区别？什么时候使用？**

数组长度固定，内存连续、访问开销小，适合出生点、固定技能槽、固定缓冲区等数量已知的场景。`List<T>` 是动态数组，内部容量不足时会扩容，适合敌人列表、背包、任务列表等数量经常变化的场景。

```csharp
int[] points = { 10, 20, 30 };
Debug.Log(points.Length);

List<int> scores = new List<int>(16); // 可提前设置容量
scores.Add(10);
scores.Remove(10);
Debug.Log(scores.Count);
```

数组可以用 `Clone` 复制第一层；`new List<T>(oldList)` 也只复制列表容器，如果元素本身是 class，元素对象仍可能被多个列表共享。高频代码中应合理设置 `List<T>` 容量，减少扩容和 GC；不要为了“统一”而把所有固定数据都改成 List。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q8：async/await 的原理？Unity 中使用要注意什么？**

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



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
**Q9：const、readonly、静态构造函数各有什么特点？**

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


> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。

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

面试答题时要强调：生命周期不是一条“所有对象严格同步”的单线程列表。Unity 会保证同一批对象的 `Awake` 先于 `Start`，但对象实例化、场景加载和脚本执行顺序可能改变具体时机。跨对象初始化不要依赖隐含顺序，应该使用显式初始化入口或启动流程管理器。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
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

`Awake` 适合做“我自己准备好”，例如缓存组件、初始化默认字段；`Start` 适合做“我开始和其他对象协作”。如果必须保证多个系统顺序，使用 Script Execution Order 只是补救，更推荐让 `GameRoot` 按阶段显式调用各模块初始化。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
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

输入采样一般放在 `Update`，再把输入结果缓存给 `FixedUpdate` 使用；否则低帧率或高帧率下可能漏掉短按输入。相机跟随放在 `LateUpdate` 是为了读取本帧最终位置，但网络插值、动画更新等情况仍要根据实际执行顺序验证。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
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

`GetComponent` 不一定是“不能用”，问题在于不应在高频路径重复查找。低频初始化调用一次通常没有问题；在 `Update`、物理循环或大量对象循环中，应缓存引用。`[RequireComponent]` 只能保证组件存在，不能保证引用对象的业务状态已经初始化。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q5：SetActive(false) 和 enabled=false 的区别？协程会停止吗？**

`SetActive(false)` 禁用整个 GameObject（含子物体），触发 `OnDisable`，并会停止挂在该 GameObject 上的协程；`enabled=false` 只禁用该组件（`Update` 不再调用），不会停止协程。协程也可以通过 `StopCoroutine`/`StopAllCoroutines` 手动停止。

```csharp
gameObject.SetActive(false);   // 整棵子树隐藏，OnDisable 触发
enabled = false;               // 只停脚本回调

IEnumerator Loop() {
    while (true) {
        Debug.Log("tick");
        yield return new WaitForSeconds(1);
    }
}
// SetActive(false) 后，挂在该 GameObject 上的协程会停止执行
```

`SetActive(false)` 会影响整棵 GameObject 子树，并触发相关组件的 `OnDisable`；`enabled=false` 只影响当前组件的消息回调。事件反注册通常放在 `OnDisable`，这样对象反复启用/禁用时不会重复订阅。若协程属于其他组件或其他 GameObject，不能简单认为禁用当前脚本就会停止它。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
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

`DontDestroyOnLoad` 适合真正的跨场景根对象，例如音频、存档、网络会话管理器；不要把临时 UI 或场景对象全部放进去，否则会形成“常驻对象越来越多”的伪内存泄漏。单例还要处理重复实例、退出时清理和测试场景隔离。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q7：Destroy 和 DestroyImmediate 有什么区别？**

`Destroy` 延迟到当前帧末执行，安全；`DestroyImmediate` 立即销毁，可能破坏渲染顺序或导致引用悬空，只在编辑器工具/特定场景使用。释放资源用 `Destroy`，配合对象池复用。

```csharp
Destroy(gameObject);          // 帧末销毁，推荐
DestroyImmediate(obj);        // 立即销毁，仅编辑器等特殊情况

// 对象池释放对象时更推荐直接 SetActive(false)
pool.Release(obj);
```

运行时优先使用 `Destroy`，因为 Unity 会在安全时机处理对象销毁；`DestroyImmediate` 主要用于编辑器脚本。对象销毁后，C# 引用变量不一定立刻变成普通 `null`，Unity 对象重载了相等运算，排查空引用时要注意“假 null”现象。

---


> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。

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

协程的关键不是“开线程”，而是保存执行位置。`yield return null` 表示至少等到下一帧，`WaitForSeconds` 受 `Time.timeScale` 影响，暂停菜单通常要使用 `WaitForSecondsRealtime`。协程中的一段普通代码仍会在主线程连续执行，不能用协程解决 CPU 密集型死循环。



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
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

线程适合计算，协程适合编排主线程上的时间流程。子线程不能直接访问 `Transform`、`GameObject`、`Debug` 等大部分 Unity API；常见做法是在线程中生成纯 C# 数据，再通过线程安全队列由主线程 `Update` 消费。线程池任务还要处理异常、取消和对象销毁后的回调。



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
**Q3：如何启动和停止协程？SetActive(false) 会停止协程吗？**

用 `StartCoroutine` 启动；`StopCoroutine`/`StopAllCoroutines` 停止；销毁 GameObject 自动停止。`SetActive(false)` 会停止挂在该 GameObject 上的协程，而 `enabled=false` 不会停止协程。

```csharp
IEnumerator timer = Countdown();
StartCoroutine(timer);
StopCoroutine(timer);          // 传 IEnumerator 引用停止
StopAllCoroutines();           // 停止该 MonoBehaviour 上所有协程

// 注意：字符串方式 StartCoroutine("Countdown") 停止也要用同名
```

推荐保存 `Coroutine` 或 `IEnumerator` 引用，而不是使用字符串形式。停止协程前要明确它属于哪个 `MonoBehaviour`；`StopAllCoroutines` 只会停止当前脚本实例上的协程。场景切换、对象禁用和业务取消都应该有清晰的停止策略。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
**Q4：WaitForSeconds 每次 new 会产生 GC 吗？怎么优化？**

会。`WaitForSeconds` 是引用类型，每次 `new` 都分配堆内存。高频使用应缓存复用。

```csharp
// 差：每次生成新对象
while (true) { yield return new WaitForSeconds(1f); }

// 好：缓存复用
static readonly WaitForSeconds oneSec = new WaitForSeconds(1f);
while (true) { yield return oneSec; }
```

缓存 `WaitForSeconds` 只适用于等待时长不变的情况；动态时长仍需创建新的等待指令，或者使用计时器累加 `Time.deltaTime`。注意静态缓存会一直存活，普通小对象影响不大，但不要把带有场景引用的对象放进静态字段。



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
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

真实项目还要处理超时、取消、重试、断网和对象销毁。下载完成后要检查 `req.result`，不要只判断 HTTP 状态；进度条更新可以节流，避免每帧刷新复杂 UI。`using` 负责释放请求对象，但不会替你管理下载资源的缓存和版本。



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
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

协程适合依赖 Unity PlayerLoop 的流程；`Task`/`UniTask` 更适合可组合的异步任务。选择时重点比较异常传播、取消、生命周期绑定和主线程切换，而不是简单认为“新 API 一定更快”。


> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。

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

触发回调的前提还受 Rigidbody 类型、碰撞层矩阵和 `isTrigger` 影响。触发器通常至少需要一方带 Rigidbody；物理碰撞回调中的 `Collision` 还包含接触点、法线和相对速度，可用于受击方向、音效和反弹计算。



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
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

速度、力和位置代表不同的控制意图：`velocity` 适合直接控制速度，`AddForce` 适合模拟力，`MovePosition` 适合运动学刚体。不要在同一个对象上同时用物理速度和 Transform 位置硬改，否则容易出现穿透、抖动和网络状态不一致。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
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

`NonAlloc` 只是不在调用时创建结果数组，并不意味着结果永远完整；命中数量超过数组容量时会被截断，所以要根据业务设置容量或做溢出策略。还应使用 LayerMask、最大距离和合适的 QueryTriggerInteraction 减少无效检测。



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
**Q4：Rigidbody 的 Interpolation 是解决什么问题的？**

物理在固定步长（默认 50Hz）更新，渲染帧率可能不同步，导致刚体运动抖动。`Interpolate`（插值）在两个物理帧之间平滑过渡，`Extrapolate`（外推）预测下一帧位置。被跟随的目标（如玩家角色）通常开启。

```csharp
rb.interpolation = RigidbodyInterpolation.Interpolate;
```

插值主要改善渲染观感，不会提高物理模拟精度。物理结果仍由 Fixed Timestep 决定；如果出现穿透，要检查碰撞检测模式、速度、刚体尺寸和物理步长，而不是只打开 Interpolation。



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
**Q5：CharacterController 和 Rigidbody 怎么选？**

`CharacterController` 自带碰撞与斜坡/台阶处理，适合人形角色，但不受物理力影响，需手动处理重力；`Rigidbody` 走完整物理模拟，适合有受力、碰撞反弹的物体（子弹、箱子、受击位移的角色）。

```csharp
// CharacterController 方案
cc.Move((moveDir * speed + Vector3.down * gravity * Time.deltaTime) * Time.deltaTime);

    // Rigidbody 方案
    rb.velocity = new Vector3(input.x * speed, rb.velocity.y, input.y * speed);
```

`CharacterController` 的移动、重力和斜坡规则由代码负责，确定性和手感较容易控制；`Rigidbody` 更符合物理世界，但角色控制、网络同步和防翻滚需要更多约束。面试中应先说项目需求，再说方案，不要绝对断言某一种永远更好。



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
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

碰撞矩阵是第一层过滤，代码中的 LayerMask 是第二层过滤；两者配合可以降低物理查询和回调数量。物理材质的摩擦、弹性会影响移动手感，调参时要同时观察质量、速度、碰撞检测模式和 Fixed Timestep。

---


> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。

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



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
**Q2：纹理内存怎么计算？移动端用什么压缩格式？**

纹理内存 ≈ 宽 × 高 × 每像素字节。RGBA32 为 4 字节/像素；ETC2/ASTC 4x4 约 1 字节/像素；开启 Mipmap 总内存约为基准的 1.33 倍。移动端推荐 ASTC（质量好、块尺寸灵活）。

```csharp
// 1024x1024 RGBA32:     1024 * 1024 * 4 = 4 MB
// 1024x1024 ASTC 4x4:   1024 * 1024 * 1 = 1 MB
// 带 Mipmap 约再乘 1.33

Texture2D tex = new Texture2D(1024, 1024, TextureFormat.RGBA32, true); // 带 mipmap
```



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
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



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
**Q4：如何控制帧率和垂直同步？**

PC 上 `QualitySettings.vSyncCount` 与显示器刷新率同步；移动端关闭垂直同步，用 `Application.targetFrameRate` 限帧省电。

```csharp
Application.targetFrameRate = 60;       // 移动端限帧
QualitySettings.vSyncCount = 1;         // PC 垂直同步（0 关闭，1 开）
Screen.sleepTimeout = SleepTimeout.NeverSleep;   // 游戏常亮
```



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
**Q5：URP、HDRP、内置渲染管线怎么选？**

URP：轻量、跨平台、移动端友好，SRP Batcher 提升合批；HDRP：高质量物理渲染，面向 PC/主机，移动端开销大；内置管线：兼容性最好但维护中。选型看目标平台和画面需求。

```csharp
// URP 中开启/关闭后处理（Volume）
var volume = GetComponent<Volume>();
volume.profile.TryGet<Bloom>(out var bloom);
bloom.intensity.value = 1.5f;
```


> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。

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



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
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



> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。
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



> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。
**Q4：法线贴图的原理？为什么要在切线空间采样？**

法线贴图把高模细节存成切线空间的法线扰动，让低模表面呈现凹凸光影。切线空间法线与表面方向无关，可平铺、可压缩（只存 XY 推导 Z），所以贴图存切线空间。

```hlsl
// 切线空间法线：采样的法线扰动
float3 normalTS = UnpackNormal(tex2D(_BumpMap, i.uv));      // xy → 法线
float3 normalWS = normalize(i.tangentWS * normalTS.x + i.bitangentWS * normalTS.y + i.normalWS * normalTS.z);
half ndotl = saturate(dot(normalWS, lightDirWS));
```



> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。
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



> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。
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

---


> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。

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



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
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



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
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



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
**Q4：UI 卡顿的常见原因？如何优化合批？**

原因：Canvas 重建频繁（改文本/颜色/位置/尺寸）、合批被打断、Mask 过多、Overdraw、文本过多。优化：动静分离 Canvas、相同图集元素相邻、TMP 文本、关闭无用 `RaycastTarget`、`RectMask2D` 代替 Mask、用 `CanvasGroup` 做整体隐藏/淡入淡出。

```csharp
// 动静分离：频繁变化的 UI 单独放一个 Canvas，避免整个大 Canvas 频繁重建
// 隐藏 UI 用 CanvasGroup，避免 SetActive 触发重建
canvasGroup.alpha = 0;
canvasGroup.interactable = false;
canvasGroup.blocksRaycasts = false;
```



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
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



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
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


> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。

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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
**Q4：热更新方案有哪些？HybridCLR 的原理是什么？**

逻辑热更：xLua/toLua（Lua 解释执行）、ILRuntime（C# 解释执行）、HybridCLR（IL2CPP 下补充元数据 + 解释执行，性能接近 AOT）。资源热更：AssetBundle + 版本清单 + 增量下载。

```csharp
// HybridCLR：把热更 DLL 转成字节数组后加载
byte[] hotfixDll = File.ReadAllBytes(Application.persistentDataPath + "/hotfix.dll");
Assembly.Load(hotfixDll);   // 正常 Assembly.Load 即可（元数据已补充）
```



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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

---


> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。

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



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
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



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
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



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
**Q4：如何用 Profiler 定位性能问题？**

CPU 模块看主线程/渲染线程/脚本耗时，找热点函数；Rendering 看 Draw Call 与三角形数；Memory 看托管堆和资源内存；GC Alloc 列抓分配；真机 Profiler 验证实际帧率与内存。

```csharp
// 代码打点定位耗时
var sw = System.Diagnostics.Stopwatch.StartNew();
DoHeavy();
sw.Stop();
Debug.Log("DoHeavy: " + sw.ElapsedMilliseconds + "ms");
```



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
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



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
**Q6：如何评估和优化移动端内存？**

关注：纹理（ASTC 压缩、限制尺寸、图集）、网格（减面、LOD）、音频（压缩）、Shader 变体、托管堆。用 Memory Profiler 打快照对比"进入/离开场景"判断是否泄漏。

```csharp
// 纹理导入设置：移动端推荐
TextureImporter importer = (TextureImporter)AssetImporter.GetAtPath(path);
importer.textureCompression = TextureImporterCompression.CompressedHQ;  // ASTC
importer.maxTextureSize = 1024;
```


> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。

---

## 10. 动画系统

**Q1：Animator 状态机怎么用？Trigger 和 Bool 参数的区别？**

状态机管理 Idle/Walk/Run/Attack 等状态和转换条件。`Trigger` 是一次性触发（使用后自动复位），适合攻击、受击；`Bool` 是持续状态，适合接地、跑步。

```csharp
animator.SetTrigger("Attack");            // 一次性，自动复位
animator.SetBool("IsGrounded", isGrounded); // 持续状态
animator.SetFloat("Speed", speed);          // 连续值
```



> **学习扩展：** 动画题回答顺序可以是资源组织、状态切换、参数驱动、混合与性能。要注意动画事件依赖剪辑、Root Motion 依赖角色控制方案，多角色场景还要考虑 Animator 数量、Update Mode、剔除和骨骼更新成本。
**Q2：Blend Tree 解决什么问题？如何驱动？**

Blend Tree 根据参数在多个动画之间平滑混合，避免状态切换生硬。例如根据速度混合走/跑，根据方向混合移动动画。

```csharp
// 2D 混合：横向速度 + 纵向速度
animator.SetFloat("MoveX", input.x);
animator.SetFloat("MoveY", input.y);

// 1D 混合：速度大小
animator.SetFloat("Speed", rb.velocity.magnitude);
```



> **学习扩展：** 动画题回答顺序可以是资源组织、状态切换、参数驱动、混合与性能。要注意动画事件依赖剪辑、Root Motion 依赖角色控制方案，多角色场景还要考虑 Animator 数量、Update Mode、剔除和骨骼更新成本。
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



> **学习扩展：** 动画题回答顺序可以是资源组织、状态切换、参数驱动、混合与性能。要注意动画事件依赖剪辑、Root Motion 依赖角色控制方案，多角色场景还要考虑 Animator 数量、Update Mode、剔除和骨骼更新成本。
**Q4：多角色场景怎么优化动画性能？**

限制 Animator 数量、设置 Culling Mode（视锥外不更新骨骼）、动画压缩、LOD 切换网格。

```csharp
// 视锥外停止更新骨骼变换，仍保留根位置
animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;

// 完全剔除（不可见且不在视锥内不更新）
// animator.cullingMode = AnimatorCullingMode.CullCompletely;
```



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
**Q5：Root Motion 和代码移动怎么选？**

Root Motion：位移由动画驱动，动作与位移天然一致，适合受击位移、连招；代码移动：位移由逻辑控制，适合玩家操控、网络同步。二者不要混用（关掉 `Apply Root Motion` 再代码移动）。

```csharp
// 代码移动时关闭 Root Motion
animator.applyRootMotion = false;

// 逻辑移动
transform.position += moveDir * speed * Time.deltaTime;
```

---


> **学习扩展：** 动画题回答顺序可以是资源组织、状态切换、参数驱动、混合与性能。要注意动画事件依赖剪辑、Root Motion 依赖角色控制方案，多角色场景还要考虑 Animator 数量、Update Mode、剔除和骨骼更新成本。

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



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
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



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
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



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
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



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
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



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
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


> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。

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



> **学习扩展：** 设计模式题不要只背类图，要说明它解决的依赖或变化点，以及引入后的代价。Unity 中尤其要补充生命周期、反注册、线程安全、重复实例和测试难度，否则全局事件或单例很容易变成隐性耦合。
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



> **学习扩展：** 设计模式题不要只背类图，要说明它解决的依赖或变化点，以及引入后的代价。Unity 中尤其要补充生命周期、反注册、线程安全、重复实例和测试难度，否则全局事件或单例很容易变成隐性耦合。
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



> **学习扩展：** 动画题回答顺序可以是资源组织、状态切换、参数驱动、混合与性能。要注意动画事件依赖剪辑、Root Motion 依赖角色控制方案，多角色场景还要考虑 Animator 数量、Update Mode、剔除和骨骼更新成本。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 设计模式题不要只背类图，要说明它解决的依赖或变化点，以及引入后的代价。Unity 中尤其要补充生命周期、反注册、线程安全、重复实例和测试难度，否则全局事件或单例很容易变成隐性耦合。
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

---


> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。

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



> **学习扩展：** 算法题先说明数据结构、不变量和复杂度，再写核心代码，最后讨论边界输入。游戏场景还要补充内存布局、每帧调用次数、是否允许分帧和是否需要预分配，不能只比较理论 Big-O。
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



> **学习扩展：** 算法题先说明数据结构、不变量和复杂度，再写核心代码，最后讨论边界输入。游戏场景还要补充内存布局、每帧调用次数、是否允许分帧和是否需要预分配，不能只比较理论 Big-O。
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



> **学习扩展：** 算法题先说明数据结构、不变量和复杂度，再写核心代码，最后讨论边界输入。游戏场景还要补充内存布局、每帧调用次数、是否允许分帧和是否需要预分配，不能只比较理论 Big-O。
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



> **学习扩展：** 算法题先说明数据结构、不变量和复杂度，再写核心代码，最后讨论边界输入。游戏场景还要补充内存布局、每帧调用次数、是否允许分帧和是否需要预分配，不能只比较理论 Big-O。
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


> **学习扩展：** 算法题先说明数据结构、不变量和复杂度，再写核心代码，最后讨论边界输入。游戏场景还要补充内存布局、每帧调用次数、是否允许分帧和是否需要预分配，不能只比较理论 Big-O。

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



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
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



> **学习扩展：** 设计模式题不要只背类图，要说明它解决的依赖或变化点，以及引入后的代价。Unity 中尤其要补充生命周期、反注册、线程安全、重复实例和测试难度，否则全局事件或单例很容易变成隐性耦合。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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



> **学习扩展：** 架构题建议从模块边界、依赖方向、生命周期、错误处理和可测试性回答。把配置、资源、事件、UI 和业务逻辑分层后，重点是让依赖可替换、状态可追踪、启动顺序可控，而不是堆叠管理器类名。
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


> **学习扩展：** 架构题建议从模块边界、依赖方向、生命周期、错误处理和可测试性回答。把配置、资源、事件、UI 和业务逻辑分层后，重点是让依赖可替换、状态可追踪、启动顺序可控，而不是堆叠管理器类名。

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



> **学习扩展：** 工具题要说明它解决的具体痛点以及适用边界：UniTask 解决异步组合和取消，Addressables 解决资源依赖与生命周期，热更新工具解决发布周期。还要关注版本兼容、AOT 裁剪、调试和失败回退。
**Q2：UniTask 相比协程有什么优势？**

无 `YieldInstruction` 堆分配、支持取消/超时/异常、可组合、自动切回主线程。适合替代协程做异步加载、倒计时、UI 流程。

```csharp
async UniTaskVoid Demo() {
    await UniTask.Delay(TimeSpan.FromSeconds(1), cancellationToken: ct);
    await button.OnClickAsync();                       // 等待点击
    await Addressables.InstantiateAsync("enemy", parent);  // 异步加载
}
```



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
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



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
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

---


> **学习扩展：** 工具题要说明它解决的具体痛点以及适用边界：UniTask 解决异步组合和取消，Addressables 解决资源依赖与生命周期，热更新工具解决发布周期。还要关注版本兼容、AOT 裁剪、调试和失败回退。

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



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
**Q2：Awake 和 Start 的执行时机？**

Awake 在创建时立即执行（未启用也执行）；Start 在首帧 Update 前执行（要求启用）。同一帧先全部 Awake 再全部 Start。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
**Q3：Update、FixedUpdate、LateUpdate 怎么用？**

FixedUpdate 固定步长处理物理；Update 处理输入与逻辑；LateUpdate 相机跟随。移动刚体放 FixedUpdate，用 velocity/MovePosition。



> **学习扩展：** 回答这类生命周期题时，先说明“什么时候调用”，再说明“适合放什么逻辑”，最后补充对象禁用、销毁和跨场景时的边界。实际项目中不要依赖隐含的脚本顺序，关键初始化应由启动流程或显式依赖管理。
**Q4：协程和线程的区别？**

协程主线程协作式、可挂起不能并行；线程真并行，但 Unity API 只能在主线程调用。



> **学习扩展：** 面试追问通常会问取消、异常和生命周期：协程仍运行在主线程，必须明确谁启动、谁停止、对象销毁后是否还需要继续。耗时计算不要只换成协程，应考虑 Task、Job System 或 Burst。
**Q5：OnTriggerEnter 和 OnCollisionEnter 触发条件？**

双方 Collider + 至少一方 Rigidbody；勾选 IsTrigger 走 Trigger（无物理阻挡），否则 Collision。



> **学习扩展：** 回答物理题要把“物理配置、执行时机、查询过滤、性能”串起来：LayerMask 和碰撞矩阵先过滤，FixedUpdate 处理刚体，NonAlloc 处理高频查询。遇到抖动或穿透时，要同时检查速度、碰撞检测模式、刚体尺寸和时间步长。
**Q6：什么是 Draw Call？怎么优化？**

CPU 提交绘制命令的次数。优化：静态/动态合批、GPU Instancing、SRP Batcher、图集、LOD、剔除。

```csharp
// GPU Instancing 关键代码
Graphics.DrawMeshInstanced(mesh, mat, matrices, count);
```



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
**Q7：AssetBundle 怎么避免内存泄漏？**

引用计数管理 + 依赖先加载 + 归零才 Unload；`Unload(false)` 保留已加载资源，`Unload(true)` 全卸（慎用）。生产环境优先 Addressables。



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
**Q8：如何降低 GC？**

避免装箱、字符串拼接、每帧 new；对象池复用；缓存 WaitForSeconds/组件引用；NonAlloc 物理查询；Profiler 抓 GC Alloc。



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
**Q9：帧同步怎么保证确定性？**

逻辑与表现分离；浮点用定点数；统一随机种子；固定迭代顺序；输入指令序列一致。

```csharp
// 定点数：用 long 表示小数，避免 float 平台差异
long raw = (long)(value * 65536f);
```



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
**Q10：移动端性能瓶颈通常在哪？**

Overdraw/填充率、纹理带宽与内存、托管堆 GC、CPU 脚本、合批失败、Shader 复杂度、热更解释执行开销。用真机 Profiler 定位。



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
**Q11：UI 卡顿的原因与优化？**

Canvas 重建频繁、合批被打断、Mask 过多、Overdraw。优化：动静分离 Canvas、TMP、关无用 RaycastTarget、RectMask2D、CanvasGroup 淡入淡出。



> **学习扩展：** UI 题重点是 Canvas 重建、合批、Overdraw、布局系统和生命周期。优化时先用 Profiler 找出是 Rebuild、Rebatch、网格数量还是贴图切换，再决定动静分 Canvas、关闭 RaycastTarget、使用图集或做虚拟化列表。
**Q12：纹理内存怎么算？**

宽 × 高 × 字节/像素；RGBA32 = 4B，ASTC 4x4 ≈ 1B；Mipmap 约 ×1.33。

```csharp
// 1024x1024 RGBA32 = 4MB
```



> **学习扩展：** 渲染题建议按 CPU 瓶颈、GPU 瓶颈、带宽和内存四个方向回答。不能只说“减少 DrawCall”，还要说明合批条件、材质/纹理切换、Overdraw 和目标平台，并用 Frame Debugger、Profiler 或 Rendering Statistics 验证。
**Q13：热更新原理？**

资源用 AssetBundle + 版本清单增量下载；逻辑用 xLua/HybridCLR/ILRuntime；启动检查版本 → 下载 → 加载新资源/代码。



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
**Q14：ZWrite 和 ZTest 的作用？**

ZTest 深度测试条件（默认 LEqual）；ZWrite 是否写深度。透明物体关 ZWrite、Queue=Transparent、从远到近渲染。



> **学习扩展：** Shader 题要从渲染管线阶段、坐标空间和深度/混合状态解释，而不是只背代码。出现透明排序、法线错误或 Shader 变体爆炸时，应分别检查 ZWrite/ZTest、切线空间、关键字数量和构建收集策略。
**Q15：如何实现对象池？**

预创建 + 复用 + 容量上限 + 状态重置；高频对象（子弹/特效/UI Item）避免 Instantiate/Destroy 开销。

```csharp
public T Get() {
    var obj = pool.Count > 0 ? pool.Pop() : Create();
    obj.gameObject.SetActive(true);
    return obj;
}
```



> **学习扩展：** 资源题要同时说明加载、缓存、依赖、引用计数、卸载和版本更新。任何资源系统都要回答“谁持有引用、何时释放、重复加载怎么办、下载失败怎么办”，否则只讲 API 仍不算完整方案。
**Q16：Mono 和 IL2CPP 的区别？**

Mono JIT：启动快、调试好、包体小，iOS 受限；IL2CPP：IL 转 C++ 原生，性能稳、包体大、构建慢，移动端默认。



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q17：Time.timeScale 影响什么？**

影响 deltaTime、FixedUpdate 频率、WaitForSeconds；不影响 WaitForSecondsRealtime 和 Update 本身调用。

```csharp
Time.timeScale = 0f;      // 暂停游戏（UI 用不受缩放的时间）
Time.timeScale = 1f;      // 恢复
```



> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
**Q18：如何排查内存泄漏？**

Profiler Memory 快照对比；检查事件反注册、静态引用、协程、AB 卸载、单例持有。

```csharp
void OnDisable() => EventCenter.Remove("key", handler);   // 记得反注册
```



> **学习扩展：** 性能题不能只列优化清单，应该先测量再修改：用 Profiler/Memory Profiler 找到具体调用和 GC Alloc，确认真机复现后再做缓存、对象池、NonAlloc 或批处理。优化后要回归 CPU、GPU、内存和功耗，避免局部优化造成整体复杂度上升。
**Q19：客户端如何做网络同步的平滑表现？**

状态同步用插值（快照间线性插值）+ 客户端预测；帧同步用延迟缓冲对齐输入。

```csharp
transform.position = Vector3.Lerp(from, to, (time - t0) / dt);
```



> **学习扩展：** 网络题要区分可靠性、顺序性、延迟、带宽和一致性，再选择 TCP、UDP、KCP 或同步模型。客户端预测、插值、重连和安全校验都不能只放在客户端，最终权威状态应由服务器确认。
**Q20：如何设计技能系统？**

配置驱动 + 状态机/行为树：技能配置表（伤害/范围/CD）+ 技能流程状态 + 事件回调（命中检测、特效、音效）。

```csharp
// 配置驱动：同一套代码，不同配置 = 不同技能
var cfg = skillMap[skillId];
StartCoroutine(CastSkill(cfg.castTime, cfg.damage, cfg.range));
```


> **学习扩展：** 通用答题模板：先给一句准确定义，再用一段最小代码说明，随后说项目中的使用场景，最后补充性能、生命周期或异常边界。面试官继续追问时，优先用真实项目中的取舍和验证方式回答。
