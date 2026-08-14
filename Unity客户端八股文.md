# Unity 客户端八股文

> 面向 Unity 客户端 / 游戏开发岗位的面试复习资料，覆盖 C#、引擎、图形学、Shader、UGUI、资源与热更、性能优化、网络、设计模式、算法等高频考点。适合系统性复习与面试前速查。

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

### 1.1 值类型与引用类型

- **值类型**：`struct`、`enum`、基本类型（`int/float/bool/char` 等）。局部变量存储在栈上，赋值是**拷贝**。
- **引用类型**：`class`、`string`、数组、委托、接口。对象在堆上，栈上只存引用，赋值传递引用。
- 值类型转成 `object` 或接口时发生**装箱**（堆分配 + 拷贝），有 GC 压力。

### 1.2 装箱与拆箱

- 装箱：值类型 → `object`/接口，在堆上分配并拷贝值。
- 拆箱：`object` → 值类型，要求运行时类型匹配。
- 危害：产生堆分配、增加 GC。常见来源：非泛型集合（`ArrayList`/`Hashtable`）、`string.Format` 传值类型、值类型赋给 `object`。
- 优化：用泛型集合、避免不必要的 `object` 转换、`string` 拼接用 `StringBuilder`。

### 1.3 string 与 StringBuilder

- `string` 不可变，任何修改都会创建新对象；大量拼接会产生大量垃圾。
- 循环拼接用 `StringBuilder`（内部字符缓冲区，可扩容）。
- `==` 比较的是**内容**（`string` 重载了运算符），`ReferenceEquals` 比较引用。
- 字符串驻留（Intern）：相同字面量共享实例，运行时动态拼出来的字符串不会自动驻留。

### 1.4 委托与事件

- 委托：类型安全的函数指针，支持多播（`+=`/`-=`）。
- 事件：委托的封装，外部只能 `+=`/`-=`，不能直接调用 `Invoke`，适合发布-订阅解耦。
- 预定义委托：`Func<...>`（有返回值）、`Action<...>`（无返回值）。
- 注意：委托/事件持有目标对象引用，忘记反注册会造成内存泄漏（如静态事件引用 MonoBehaviour）。

### 1.5 泛型

- 编译期类型安全，值类型用泛型可**避免装箱**。
- 约束：`where T : class / struct / new() / 基类 / 接口`。
- 协变/逆变：`IEnumerable<out T>`、`Action<in T>`。
- 注意：泛型静态类每个 T 组合有独立的静态字段。

### 1.6 反射与特性

- 反射：运行时获取类型信息、创建对象、调用方法、读写字段。性能开销大，应缓存 `Type`、`MethodInfo`、`FieldInfo` 等结果。
- 特性（Attribute）：给代码加元数据，配合反射使用。Unity 常用：`[SerializeField]`、`[Header]`、`[Range]`、`[RequireComponent]`、`[DisallowMultipleComponent]`。
- 使用场景：序列化扩展、编辑器工具、配置驱动、框架（如 ORM、依赖注入）。

### 1.7 托管 GC

- 托管堆分代：0 代（新对象，回收最频繁）、1 代、2 代（老对象）；大对象堆（LOH，>85KB）不压缩。
- 触发时机：0 代满、显式 `GC.Collect()`、LOH 满、系统内存压力。
- 优化方向：减少分配（对象池、避免装箱）、缩短对象生命周期、避免 `Update` 中频繁 new、避免持有大数组。
- Unity 支持增量式 GC（Incremental GC），把回收分散到多帧，减少卡顿。

### 1.8 async / await

- 本质是编译器生成的状态机（`IAsyncStateMachine`），不阻塞线程。
- Unity 中注意：`async void` 异常会导致崩溃/难以捕获；MonoBehaviour 销毁后回调仍在执行会访问失效对象；注意线程切换回主线程（Unity API 只能在主线程调用）。
- `Task.Run` 走线程池，适合耗时计算，但要线程安全。

### 1.9 其他高频点

- `const` 编译期常量（必须字面量）；`readonly` 运行时只读（构造中可赋值）。
- `sealed` 密封类不可继承；`abstract` 抽象类不可实例化；`virtual`/`override` 实现多态。
- 静态构造函数：首次访问静态成员时执行且只执行一次；静态类不能实例化。
- 索引器：`this[int index]`。
- 深拷贝 vs 浅拷贝：浅拷贝复制引用；深拷贝复制内容（实现 `ICloneable` 或序列化实现）。
- 可空类型 `int?`，`?.` 空条件、`??` 空合并、`??=`。
- LINQ：延迟执行（`IEnumerable`），注意闭包捕获与每帧调用时的分配；`IQueryable` 用于表达式树（数据库查询）。
- `switch` 表达式、模式匹配（`is`、`switch` 模式）。
- `using` 语句：`IDisposable` 自动释放，本质是 try/finally。

---

## 2. Unity 生命周期与脚本

### 2.1 MonoBehaviour 生命周期

- `Awake`：脚本实例创建时调用（**无论组件是否启用**），用于初始化字段、注册事件、获取组件引用。
- `OnEnable`：对象每次激活时调用（含首次 `SetActive(true)`、`Instantiate`、`AddComponent`）。
- `Start`：第一帧 `Update` 之前调用一次，要求组件启用；用于依赖其他对象的初始化。
- `FixedUpdate`：固定时间步调用（默认 0.02s = 50 次/秒），处理物理逻辑。
- `Update`：每帧调用，处理游戏逻辑（与帧率相关）。
- `LateUpdate`：`Update` 之后调用，适合相机跟随。
- `OnDisable`：组件被禁用或对象 `SetActive(false)` 时调用。
- `OnDestroy`：对象销毁时调用。
- `OnApplicationPause` / `OnApplicationQuit`：应用切后台/退出。
- `OnGUI`：每帧多次（布局、绘制、输入事件），性能差，尽量避免用于游戏 UI。

**执行顺序要点**

- 同一帧内：先执行场景中所有 `Awake`，再执行所有 `Start`。
- `Instantiate` 出来的对象，其 `Awake` 在实例化时同步执行。
- `OnEnable` 与 `Awake` 顺序：`Awake` 先于 `OnEnable`（如果都触发）。
- `Destroy` 延迟到当前帧末执行；`DestroyImmediate` 立即执行（编辑器工具慎用）。

### 2.2 Update / FixedUpdate / LateUpdate 对比

| 方法 | 调用频率 | 用途 |
| --- | --- | --- |
| `FixedUpdate` | 固定步长，与帧率无关（默认 50Hz） | 物理、移动刚体 |
| `Update` | 每帧，帧率相关 | 常规逻辑、输入检测 |
| `LateUpdate` | 每帧，Update 后 | 相机跟随、需要最后更新的逻辑 |

- `Time.deltaTime`：上一帧耗时；`Time.fixedDeltaTime`：固定物理步长。
- 物理更新与渲染解耦，一帧内可能执行多次 `FixedUpdate`。
- 用 `FixedUpdate` 移动刚体时使用 `Rigidbody.MovePosition`/`velocity`，不要直接改 `transform.position`。

### 2.3 GameObject、Transform、组件

- `GameObject` 是容器，功能由挂载的组件提供（Component）。
- 创建方式：`new GameObject()`、`Instantiate(prefab)`、`AddComponent<T>()`、`Resources/AssetBundle` 加载后实例化。
- `Transform` 属性访问：Unity 内部缓存，但大量查找仍昂贵，应缓存引用。
- 层级：`parent/child`；`localPosition` 相对父节点，`position` 是世界坐标。
- 预制体（Prefab）是资源模板，实例化后与原资源断开（同一份网格/材质被共享，不复制资源本身）。

### 2.4 禁用与隐藏

- `gameObject.SetActive(false)`：禁用整个对象（含子物体），触发 `OnDisable`；再次激活触发 `OnEnable`。
- `component.enabled = false`：只禁用该组件（如 `Update` 不再调用），不隐藏 GameObject。
- 注意：`SetActive(false)` 与 `enabled=false` **不会停止协程**；销毁对象才会停止。
- 隐藏 UI 推荐用 `CanvasGroup`（透明度 + 关闭射线检测）或移出屏幕，避免频繁 `SetActive` 引发 Canvas 重建。

---

## 3. 协程与异步

### 3.1 协程原理

- 协程是迭代器：`IEnumerator` + `yield return`，Unity 在内部每帧调用 `MoveNext()`，根据返回值决定何时继续。
- `yield return null`：下一帧继续；`WaitForSeconds`：等待（受 `Time.timeScale` 影响）；`WaitForSecondsRealtime`：不受缩放影响；`WaitForEndOfFrame`：帧末；`WaitUntil`：条件满足；`yield return UnityWebRequest`：请求完成。
- 协程运行在**主线程**，是协作式调度，不是并行。

### 3.2 协程与线程的区别

- 协程：单线程、可挂起恢复、无并行、适合分帧执行或异步等待回调；不能做耗时计算（会卡主线程）。
- 线程：真并行，需要锁/线程安全；Unity 引擎 API 大多只能在主线程调用。

### 3.3 协程的停止

- `StopCoroutine(name / IEnumerator)`、`StopAllCoroutines()`。
- 销毁 GameObject 自动停止该对象上的协程。
- 注意：`SetActive(false)`、`enabled = false` 不会停止协程。
- 每帧 `new WaitForSeconds` 会产生垃圾，可缓存实例。

### 3.4 网络加载与异步

- `WWW` 已过时，用 `UnityWebRequest`。
- 异步加载：`yield return request.SendWebRequest()`，完成后检查 `result`（`Success/ConnectionError/ProtocolError`）。
- 场景异步加载：`SceneManager.LoadSceneAsync`；资源异步加载：`AssetBundle.LoadFromFileAsync`、`Addressables.LoadAssetAsync`。
- 协程与 `async/await` 可结合：用 `UniTask` 框架替代协程，性能更好、无 `YieldInstruction` 分配。

---

## 4. 物理系统

### 4.1 刚体与碰撞器

- 碰撞检测前提：双方都有 `Collider`；**至少一方有 `Rigidbody`** 才会触发碰撞/触发事件。
- 静态碰撞体：只有 Collider 不移动，物理开销小（引擎内部优化）。
- 动态刚体：受物理引擎驱动（重力、力、速度）。
- Kinematic 刚体：不被物理引擎驱动，但参与碰撞，由代码移动（`MovePosition`）。
- 碰撞体形状选择：Box/Sphere/Capsule 计算快，网格碰撞体（MeshCollider）开销大，移动端慎用。
- 刚体休眠（Sleeping）：长时间静止的刚体自动休眠，减少物理计算；被碰撞/施加力时唤醒。

### 4.2 OnCollision 与 OnTrigger

- 勾选 `IsTrigger` 后走触发事件：`OnTriggerEnter/Stay/Exit`；否则走碰撞事件：`OnCollisionEnter/Stay/Exit`。
- 触发事件双方都需要 Collider，至少一方有 Rigidbody。
- Trigger 不做物理阻挡，只做范围检测（如区域、拾取、陷阱）。
- Collision 事件能拿到 `ContactPoint`、`Collision.relativeVelocity`。

### 4.3 物理更新与插值

- 物理在 `FixedUpdate` 阶段更新，默认固定步长 0.02s（50Hz），与渲染帧率解耦。
- 帧率波动时，一帧可能执行 0 次或多次 `FixedUpdate`。
- 刚体 `Interpolate`/`Extrapolate`：在物理步进与渲染帧之间插值/外推，避免物体抖动。
- 修改刚体运动：`AddForce`、`velocity`、`MovePosition`；不要直接改 `transform`（会破坏物理模拟一致性）。

### 4.4 射线检测

- `Physics.Raycast`：返回是否命中第一个对象。
- `Physics.RaycastAll`：返回所有命中（会分配数组）。
- `Physics.RaycastNonAlloc`：写入预分配数组，**避免 GC 分配**，高频射线推荐。
- `LayerMask` 过滤层级，`QueryTriggerInteraction` 控制是否检测 Trigger。
- 大量射线（如每帧检测）注意性能：减少数量、缩短距离、使用空间分区。

### 4.5 其他物理点

- 物理材质 `PhysicMaterial`：控制摩擦（Static/Dynamic Friction）与弹性（Bounciness）。
- 碰撞矩阵：Project Settings → Physics 中配置层与层之间是否碰撞/触发。
- `CharacterController`：胶囊体 + 斜坡/台阶处理，适合人形角色，不依赖刚体；用 `Move`/`SimpleMove` 移动，需自己处理重力。
- `Rigidbody` 的约束（Constraints）：锁定旋转/位移，避免抖动。
- 性能：减少碰撞体数量、用简单形状代替 MeshCollider、合理分层、控制物理查询频率。

---

## 5. 渲染与图形学

### 5.1 渲染管线

- 传统固定管线已废弃；Unity 2019.3+ 提供可编程渲染管线（SRP）。
- **URP**（Universal RP）：轻量、跨平台、移动端友好，可自定义。
- **HDRP**（High Definition RP）：高质量物理渲染，面向 PC/主机，移动端开销大。
- 内置管线（Built-in）：兼容性最好，维护中。
- 渲染流程（GPU 侧）：顶点着色器 →（可选细分/几何）→ 裁剪与光栅化 → 片元着色器 → 逐片元测试与混合。
- 渲染流程（CPU 侧）：Culling（视锥/遮挡剔除）→ 提交 Draw Call → GPU 执行。

### 5.2 Draw Call 与合批

- Draw Call：CPU 每帧向 GPU 发送的绘制命令次数；过多会卡 CPU（驱动开销）。
- **静态合批**：把静态物体网格合并后一次性绘制；减少 Draw Call，但合并网格增加内存。
- **动态合批**：运行时把满足条件的小物体合批（顶点数限制，如多数平台 300 顶点内、同材质）；CPU 有额外开销。
- **GPU Instancing**：同网格同材质的大量物体一次绘制（如草地、子弹、人群）；Shader 需声明支持 instancing。
- **SRP Batcher**：URP/HDRP 下减少材质/着色器状态切换，前提是 Shader 兼容（Inspector 显示 SRP Batcher Compatible）。
- 合批条件：相同材质（相同纹理/Shader）、相同 RenderQueue、不破坏排序。

### 5.3 剔除

- 视锥剔除（Frustum Culling）：相机视锥外的物体不提交渲染，引擎默认开启。
- 遮挡剔除（Occlusion Culling）：被完全遮挡的物体不渲染，需要烘焙遮挡数据；适合建筑密集场景。
- 层级剔除（Culling Mask）：按 Layer 控制相机渲染内容。

### 5.4 纹理

- 压缩格式：PC 用 DXT/BC7，移动端用 ETC2/ASTC；ASTC 压缩质量好、支持任意 4x4~12x12 块。
- Mipmap：为贴图生成多级渐远纹理，减少远处闪烁与锯齿；代价是内存增加约 1/3。
- 纹理内存估算：宽 x 高 x 每像素字节；RGBA32 = 4 字节，ETC2/ASTC 4x4 约 1 字节/像素。
- 图集（Sprite Atlas / Texture Atlas）：把多张小图合入一张大图，减少纹理切换、提高合批。

### 5.5 光照

- 实时光照：动态光源，开销大（逐像素光照 + 阴影）。
- 烘焙光照：静态物体预计算光照贴图（Lightmap），运行时开销小；动态物体受实时光或 Light Probe 影响。
- 全局光照（GI）：Enlighten（已逐步淘汰）/ Progressive（渐进式烘焙）；实时 GI 开销大，移动端慎用。
- 阴影：Shadow Map 技术；实时阴影有距离限制与级联（Cascaded Shadow Map），优化方式：调距离、降分辨率、烘焙静态阴影。
- Light Probe：给动态物体提供烘焙光照信息；Reflection Probe 提供反射。

### 5.6 相机与帧率

- 垂直同步（vSyncCount）：PC 上限制帧率与显示器刷新率同步；移动端通常关闭，用 `Application.targetFrameRate` 限帧省电。
- 帧率相关：掉帧（卡顿）要结合 Profiler 看 CPU/GPU 瓶颈；`FrameTime` 比平均帧率更能反映问题。
- 相机设置：`FOV`、`Clipping Planes`（近远裁剪面）、`Culling Mask`、`Clear Flags`（天空盒/纯色/深度）。

---

## 6. Shader

### 6.1 顶点 / 片元着色器

- 顶点着色器（Vertex）：处理顶点位置与属性，完成 模型空间 → 世界 → 观察 → 裁剪 空间的变换；输出 `SV_POSITION`。
- 片元着色器（Fragment/Pixel）：对每个片元计算最终颜色；在光栅化之后执行。
- 完整管线：顶点着色器 →（曲面细分 → 几何着色器，可选）→ 光栅化（插值）→ 片元着色器 → 模板/深度测试 → 颜色混合 → 帧缓冲。

### 6.2 常用语义

- `POSITION`（顶点位置）、`NORMAL`（法线）、`TEXCOORD0..n`（UV）、`TANGENT`（切线）、`COLOR`（顶点色）。
- `SV_POSITION`（裁剪空间顶点位置）、`SV_Target`（输出颜色）、`SV_Depth`。

### 6.3 渲染状态与顺序

- 渲染队列（Queue）：`Background`（天空盒等）→ `Geometry`（不透明）→ `AlphaTest` → `Transparent`（透明）→ `Overlay`（UI/后处理）。
- `ZTest`：深度测试，默认 `LEqual`；透明物体常改为 `Off` 或 `Less`。
- `ZWrite`：是否写深度缓冲；透明物体一般关闭（避免遮挡后面的透明物体）。
- 混合（Blend）：`Blend SrcAlpha OneMinusSrcAlpha` 为标准 alpha 混合；加法混合 `Blend One One`（火焰、发光）。
- 渲染顺序规则：不透明物体不排序（深度测试决定可见性）；透明物体需要**从远到近**排序（混合依赖顺序）。

### 6.4 常用光照模型

- Lambert 漫反射：`N dot L`；Half-Lambert：`N dot L * 0.5 + 0.5`，避免暗面死黑。
- Blinn-Phong 高光：半角向量 `H = normalize(L + V)`，`pow(max(N dot H, 0), gloss)`。
- PBR：基于物理，金属度（Metallic）/ 粗糙度（Roughness）工作流，微表面模型（GGX）+ Fresnel。

### 6.5 常用技术

- 法线贴图：把高模细节存成切线空间法线，在片元中采样并变换到世界/切线空间参与光照；低模获得高模细节。
- 切线空间 vs 世界空间：切线空间可压缩、可 tiling；世界空间更直观、需要矩阵变换。
- 抗锯齿：MSAA（硬件多重采样，开销大）、TAA（时间累积，动起来可能糊）、FXAA（后处理近似，快但糊）。
- 后处理：Bloom（泛光）、景深、色调映射、颜色分级；URP 中用 Renderer Feature / Full Screen Pass。
- 卡通渲染：色阶漫反射（Ramp）+ 描边（法线外扩/深度边缘检测）+ 高光裁剪。
- 视差/浮雕贴图：利用高度图模拟表面凹凸，比法线贴图更强。
- 移动端注意事项：Overdraw（填充率）是主要瓶颈；避免全屏复杂后处理；`half`/`fixed` 精度、纹理带宽、变体数量。

### 6.6 Shader 变体

- 变体（Variant）：关键字（`#pragma multi_compile`/`shader_feature`）组合出的不同版本。
- 变体过多会增大包体与构建时间；用 Shader Variant Collection 预收集、裁剪无用变体。
*** End Patch

---

## 7. UGUI

### 7.1 Canvas 渲染模式

- **Screen Space - Overlay**：UI 永远在最上层，屏幕空间，不支持被 3D 物体遮挡；最常用。
- **Screen Space - Camera**：UI 渲染到指定相机，可被 3D 物体穿插遮挡；支持 Canvas 缩放。
- **World Space**：UI 在世界空间（如血条、飘字），可旋转、缩放。
- 每个 Canvas 内部独立合批，不同 Canvas 之间不合并；Canvas 的 `SortingOrder` 决定显示顺序。
- Canvas 下的元素只要位置/尺寸/颜色/文本等发生变化，就会触发该 Canvas 的**重建（Rebuild）**，开销与 UI 元素数量相关。

### 7.2 RectTransform

- 锚点（Anchor）：UI 相对父节点的参考点；`pivot` 是自身旋转/缩放的中心点。
- 锚点四角可分别设置：stretch（拉伸）模式下 UI 会随父节点尺寸变化自适应。
- `anchoredPosition` 是相对锚点的位置；`sizeDelta` 是相对锚点的尺寸差。
- UI 自适应方案：锚点 + CanvasScaler（按参考分辨率缩放，模式：Constant Pixel Size / Scale With Screen Size）。

### 7.3 图集与合批

- Sprite Atlas：把大量 Sprite 打包进一张纹理，减少纹理切换、提高合批率。
- UGUI 合批：同一 Canvas 内，相邻层级、同材质/同图集的元素合并为一个 Draw Call；被其他元素**穿插会打断合批**。
- 优化：同图集的 UI 尽量相邻；改变层级（SiblingIndex）会触发重建；避免在 UI 树中插入异图集元素。

### 7.4 事件系统

- `EventSystem` + `GraphicRaycaster` + 组件实现接口：`IPointerClickHandler`、`IDragHandler`、`IScrollHandler` 等。
- 点击检测基于射线（GraphicRaycaster 对每个 Graphic 做命中测试），Blocking 由 `RaycastTarget` 决定。
- 事件冒泡：`ExecuteEvents.Execute` 会从被点击元素向父级传播，直到有处理者或冒泡到根。
- 提升性能：给不需要接收事件的图片关闭 `RaycastTarget`。

### 7.5 UI 性能优化

- 避免频繁修改文本（TextMeshPro）、颜色、位置、尺寸——都会触发 Canvas 重建。
- 减少 Canvas 数量但避免单个 Canvas 元素过多（重建是全量开销）；动静分离：静态 UI 与频繁变化的 UI 分开 Canvas。
- Mask 使用模板缓冲（Stencil），与 RectMask2D 相比开销更大；矩形裁剪优先用 RectMask2D。
- 文本用 TextMeshPro（SDF 渲染，性能与清晰度更好）。
- 大量 UI 淡入淡出用 CanvasGroup（只改 alpha，不破坏合批）。
- Overdraw：半透明、多层叠 UI 会增加填充开销。
- 隐藏大界面优先考虑 Canvas 关闭/CanvasGroup，而不是频繁 SetActive。

### 7.6 常用组件

- `Image`（图集 Sprite，可九宫格）、`RawImage`（任意纹理）、`Text`/`TextMeshPro`。
- 布局组件：`Horizontal/Vertical/Grid Layout Group`、`ContentSizeFitter`、`LayoutElement`（注意布局重建开销）。
- 交互：`Button`、`Toggle`、`Slider`、`ScrollRect`、`InputField`。
- `CanvasGroup`：统一控制子 UI 的透明度、是否可交互、是否阻挡射线。

---

## 8. 资源管理与热更新

### 8.1 Resources / AssetBundle / Addressables

- **Resources**：随安装包打进 `Resources` 文件夹，不可热更新；加载慢（需要解压）、不支持增量；只适合放少量配置。
- **AssetBundle**：资源可独立打包、远程下载热更；需要自己管理依赖、加载与卸载，容易泄漏。
- **Addressables**：基于 AssetBundle 的现代资源管理框架，自动处理引用计数、依赖、远程/本地加载、生命周期，推荐新项目使用。

### 8.2 AssetBundle 核心

- 打包：按更新频率 / 功能模块 / 关卡 划分包；避免依赖混乱与冗余。
- Manifest：记录包之间的依赖关系；加载资源前需先加载其依赖包。
- 加载方式：
  - `AssetBundle.LoadFromFile`：本地文件，最快。
  - `AssetBundle.LoadFromMemory`：从字节数组加载（需传入完整字节，有拷贝开销）。
  - `UnityWebRequestAssetBundle`：远程下载。
- 卸载：
  - `Unload(false)`：卸载 AB 对象，已加载的 Asset 保留（可继续使用，但重新加载同一资源可能产生重复副本，需配合引用计数）。
  - `Unload(true)`：卸载 AB 及从该 AB 加载的所有资源，已实例化对象会丢失网格/材质引用。
  - 正确姿势：引用计数 + 全局资源管理器，资源不用时递减计数，为 0 时卸载。

### 8.3 热更新方案

- **Lua 热更**：xLua / toLua，逻辑用 Lua 编写解释执行；热更灵活，性能有损，调试不便。
- **ILRuntime**：C# 解释执行热更；无需额外语言，性能一般。
- **HybridCLR**（原 huatuo）：基于 IL2CPP 的 C# 热更；补充元数据 + 解释执行，性能接近 AOT，主流选择。
- 资源热更：AssetBundle + 版本清单（version/manifest）+ 增量下载 + 本地校验。
- 热更流程：启动 → 检查版本 → 拉取版本清单 → 计算差异 → 下载 → 加载新 AB/代码 → 切换版本。
- 代码与资源热更分离：代码热更（HybridCLR/Lua）与资源热更（AB）通常是两套通道。

### 8.4 对象池

- 目的：避免频繁 `Instantiate`/`Destroy` 的创建开销与 GC 压力。
- 适用：子弹、特效、飘字、怪物、UI 元素等高频创建销毁对象。
- 实现要点：预创建 + 复用、容量上限、对象激活/隐藏时回调（`OnEnable`/`OnDisable`）、重置状态、超时回收。
- 注意：池化对象销毁时用 `Destroy` 直接释放，不要把池本身也池化（保持简单）。

### 8.5 资源生命周期管理

- 预加载：进入场景前预加载常用资源，避免运行中卡顿。
- 异步加载 + 加载进度 UI，避免阻塞主线程。
- 资源版本管理：CDN 部署 + 版本号校验 + 断点续传。
- 包体优化：剔除无用资源（Asset Bundle Browser / 引用分析）、纹理压缩、Shader 变体裁剪、音频压缩、模型减面。

---

## 9. 内存管理与性能优化

### 9.1 Unity 内存构成

- 托管堆（Mono / IL2CPP）：C# 对象，GC 管理。
- 原生内存（Native）：引擎对象（纹理、网格、音频、Shader 等），由引用计数/引擎管理。
- 资源内存：AssetBundle 加载后的资源。
- IL2CPP 与 Mono：
  - Mono：JIT 解释/即时编译，启动快、调试方便、包体小；iOS 被禁 JIT（Unity 改用 AOT）。
  - IL2CPP：IL 转 C++ 再编译成原生代码，性能更稳、包体更大、构建慢；iOS/Android 默认。
  - 两者托管堆都是 C# GC 管理，内存模型一致。

### 9.2 内存泄漏常见原因

- 事件未反注册：静态事件 / 单例事件持有已销毁对象引用。
- 静态字段持有大对象或集合持续增长。
- 协程未停止：协程持有对象引用。
- AssetBundle 未卸载 / 加载后未 `Unload`。
- `Resources.Load` 后未 `Resources.UnloadUnusedAssets`。
- 单例持有大量 UI/资源引用。
- 匿名委托/闭包捕获外部引用，被长期持有。

### 9.3 GC 优化

- 减少堆分配：避免装箱、`string` 拼接、LINQ 闭包、每帧 `new` 临时对象。
- `Update` 中避免：`Debug.Log`（大量调用）、`string.Format`、`foreach` 值类型集合装箱、反射调用。
- 对象池复用高频对象。
- 缓存 `WaitForSeconds`、组件引用、`Animator` 参数 ID。
- 用 `Physics.RaycastNonAlloc`、`Collider` 数组预分配代替 `Alloc` 版本。
- 结构体 + `Span`/`Memory` 减少分配（现代 Unity 支持 C# 8+）。
- 用 Profiler 的 GC Alloc 列定位分配热点。

### 9.4 资源与包体优化

- 纹理：压缩（ASTC/ETC2）、限制最大尺寸、Mipmap 按需、图集、共享纹理。
- 网格：减面、LOD、压缩顶点格式、剔除多余 UV/切线。
- 音频：压缩格式、采样率、循环点。
- 动画：关键帧压缩、动画纹理化（Texture Animation）。
- Shader：变体裁剪、合并 Shader 减少加载。
- 场景：拆分场景、异步加载、遮挡剔除烘焙。

### 9.5 运行性能优化清单

- 缓存 `GetComponent`/`transform` 引用，避免每帧查找。
- 避免每帧 `GameObject.Find` / `FindObjectOfType`（改为引用注入或事件）。
- 大量同构物体用 GPU Instancing / 对象池。
- 物理：减少碰撞体、用简单形状、分层、降低 `Fixed Timestep` 或提高 `Solver Iterations` 按需。
- 动画：多角色用 Animator 剔除（Culling Mode）、动画压缩。
- 音频：限制同时播放音频源数量。
- UI：见 7.5。
- 脚本执行顺序：批量驱动（自定义 Update 管理器）比每帧大量 MonoBehaviour.Update 更可控。

### 9.6 Profiler 使用

- CPU 模块：看主线程/渲染线程/脚本耗时；定位热点函数。
- Rendering：Draw Call、SetPass Call、三角形数。
- Memory：托管堆大小、纹理/网格内存、资源引用。
- GC Alloc：抓分配热点。
- Frame Debugger：逐 Draw Call 检查合批与渲染状态。
- 真机 Profiler：连设备测帧率、内存、发热（用 Snapshot / Memory Profiler 包）。
*** End Patch

---

## 10. 动画系统

### 10.1 Animator 状态机

- 状态（State）：Idle / Walk / Run / Attack 等；转换（Transition）：带条件（Float/Int/Bool/Trigger 参数）。
- 参数：`SetFloat`/`SetInt`/`SetBool`/`SetTrigger`；`Trigger` 使用后自动重置。
- 过渡（Transition）：`Has Exit Time` 是否等待当前动画播完；`Transition Duration` 过渡时长；`Interruption Source` 打断来源。
- 动画层（Layer）：基础层 + 附加层（如上半身持枪、下半身走路）；层有权重与 `Avatar Mask`（影响部位）。

### 10.2 动画混合与曲线

- Blend Tree：一维/二维混合，例如根据速度混合走/跑/冲刺，根据方向混合移动动画。
- 动画曲线（Animation Curve）：把数值随时间变化暴露给代码（如技能伤害时机、音效时机）。
- 动画事件（Animation Event）：在关键帧触发回调；注意字符串匹配开销。
- Root Motion：根骨骼位移驱动角色移动（勾选 Apply Root Motion），位移由动画决定；代码移动则关闭。

### 10.3 骨骼动画原理

- 骨骼（Bone）层级驱动蒙皮网格（SkinnedMeshRenderer），每根骨骼有变换，顶点由多个骨骼加权（Bone Weights）变形。
- 动画数据是骨骼在各关键帧的 Transform 曲线。
- 优化：动画压缩（去冗余关键帧）、动画剔除（视锥外/远离相机不更新骨骼）、LOD（降低骨骼数/切换网格）、动画纹理化。

### 10.4 Playable API 与动画优化

- Playable API：更底层灵活的动画系统（Animator 底层实现），可用于 Timeline、自定义混合、性能更高。
- 动画优化：
  - 多角色：限制 Animator 数量、Culling Mode（Always Animate / Cull Update Transforms / Cull Completely）。
  - 压缩动画、控制动画文件数量与大小。
  - 避免大量动画事件字符串查找（用整数 Hash）。
  - 技能/战斗动画用状态机 + 参数驱动，避免过度复杂的状态网络。

---

## 11. 网络编程

### 11.1 TCP vs UDP

- **TCP**：可靠、有序、面向连接、有流量控制；适合登录、结算、聊天等关键数据。
- **UDP**：无连接、不可靠、快；适合实时战斗；上层可做可靠传输（如 KCP）。
- 游戏常见组合：大厅/登录走 TCP，战斗走 UDP + KCP。
- 移动端网络：抖动、延迟、带宽受限，需客户端缓冲、服务器快照、自适应码率。

### 11.2 帧同步 vs 状态同步

- **帧同步**：服务器/主机只广播输入指令，所有客户端跑同一套逻辑，保证结果一致。
  - 优点：带宽低（只传输入）、回放容易。
  - 要求：逻辑确定性——浮点运算一致（用定点数）、统一随机种子、集合/迭代顺序固定、逻辑与表现分离、禁用于表现层做逻辑。
  - 表现预测：本地提前模拟，网络延迟用延迟缓冲对齐。
- **状态同步**：服务器权威，广播实体状态（位置、血量等），客户端只做表现。
  - 优点：开发直接、防作弊好、容错强。
  - 需要：插值（渲染平滑）、客户端预测（响应感）、服务器回滚校验（Rollback，格斗/射击常用）。
- 客户端预测 + 服务器校正：本地先执行玩家输入，收到服务器权威状态后对比校正；服务器会回滚并重放（Rollback Netcode）。

### 11.3 序列化与协议

- 序列化格式：JSON（可读、慢）、Protobuf（二进制、快、小）、自定义二进制。
- 性能：Protobuf/二进制 > JSON；考虑带宽与 GC（复用序列化缓冲）。
- 协议设计：消息 ID + 长度 + 体；版本兼容（增删字段用可扩展格式）。
- 粘包/拆包：TCP 是字节流，需要按包头长度解析；UDP 有消息边界无需处理。
- Nagle 算法会合并小包造成延迟，实时游戏可关闭（`NoDelay`）。

### 11.4 连接与可靠性

- 心跳：定期发心跳包检测断线；超时阈值 + 重连机制。
- 断线重连：重连协议、状态恢复（服务器下发快照/断线重进）。
- 丢包处理：UDP 下丢包重传（KCP 的 ARQ）、冗余发送关键包。
- 带宽估算：包大小 x 频率 x 玩家数；同步频率按需求调整（如 10~30Hz）。

### 11.5 常见网络问题

- 帧同步不同步：浮点不一致、随机数不一致、UI 表现混入逻辑、计时器不一致。
- 状态同步抖动：插值不足、快照间隔过大、客户端预测未校正。
- 移动网络：弱网策略（预测、减速、缓冲）、断线重连、战斗回放校验。

---

## 12. 设计模式

### 12.1 单例（Singleton）

- 用途：全局唯一管理器（资源、音频、事件、网络）。
- 实现：懒加载 + `Lazy<T>` / lock；MonoBehaviour 单例用 `DontDestroyOnLoad` 跨场景保留。
- 缺点：隐藏依赖、难测试、生命周期难控制；建议限制使用，用依赖注入/事件解耦代替滥用。
- 注意：场景切换时单例引用的场景对象会失效。

### 12.2 观察者 / 事件中心

- 发布-订阅解耦：模块 A 发事件，模块 B/C 订阅，互不依赖。
- Unity 实现：C# event、Action 字典事件中心（EventDispatcher）。
- 注意：订阅方销毁时要反注册，否则内存泄漏；事件参数用结构体/复用对象减少 GC。

### 12.3 对象池（Object Pool）

- 复用高频对象，避免反复创建销毁；见 8.4。

### 12.4 工厂（Factory）

- 把对象创建逻辑集中（配合资源加载、对象池、配置表）。
- 简单工厂 / 抽象工厂 / 工厂方法。

### 12.5 状态模式（State）

- 把状态行为封装成类，上下文切换状态对象（角色 Idle/Attack/Dodge、游戏 登录/加载/战斗）。
- 对比 Animator：逻辑状态机管玩法，Animator 管表现；两者可映射。
- 状态机变体：FSM、分层状态机（HFSM）、行为树（AI）、状态机+事件。

### 12.6 命令模式（Command）

- 把请求封装成对象（输入、技能、撤销/重做）。
- 帧同步中天然使用：输入即命令，记录输入序列用于回放与回滚。

### 12.7 享元（Flyweight）

- 共享不变数据：技能配置、图标、图集精灵；用字典缓存避免重复实例。
- 本质：缓存共享 + 外部状态分离。

### 12.8 其他常用

- 组件模式：Unity 本身（功能 = 组件组合）。
- 组合模式：UI 树、场景树递归处理。
- 策略模式：算法族替换（移动、伤害计算）。
- 责任链：事件冒泡、输入处理链。
- 适配器/外观：封装 SDK、平台差异（iOS/Android/WeChat）。
- 中介者：模块间通信统一走中介，避免网状依赖。
- MVC / MVVM：UI 与数据分离；Unity 常用简化版（View + Model + Presenter/ViewModel）。
*** End Patch

---

## 13. 数据结构与算法

### 13.1 高频数据结构

- 数组：连续内存、随机访问 O(1)、插入删除 O(n)。
- 链表：插入删除 O(1)（已知节点）、随机访问 O(n)。
- 栈 / 队列：LIFO / FIFO；双端队列。
- 哈希表（Dictionary/HashSet）：平均 O(1) 查询，注意扩容与哈希冲突（链地址/开放寻址）。
- 树：二叉树、二叉搜索树（BST）、平衡树（AVL/红黑树）、堆（优先队列）、字典树（Trie）。
- 图：邻接矩阵 / 邻接表；DFS/BFS。
- 复杂度：时间与空间复杂度分析，大 O 记法。

### 13.2 排序

- 快排：分治，平均 O(n log n)，不稳定，工程常用。
- 归并：稳定 O(n log n)，需额外空间；适合链表/外部排序。
- 堆排序：O(n log n) 原地，不稳定。
- 插入/冒泡/选择：O(n^2)，小规模或基本有序时可用。
- 工程场景：`List.Sort` 内部为 Introspective Sort（快排+堆+插入混合）。

### 13.3 寻路与空间结构

- BFS：无权图最短路；DFS：遍历/回溯。
- Dijkstra：带权最短路；A*：启发式搜索，`f = g + h`（g 已走代价，h 到终点估计代价，需可采纳）。
- A* 优化：二叉堆/优先队列、网格预处理、跳点搜索（JPS）。
- NavMesh：Unity 内置导航网格（烘焙可行走区域），`NavMeshAgent` 移动；适合开放世界寻路。
- 四叉树（2D）/八叉树（3D）/BVH/空间哈希：加速视野查询、碰撞检测、渲染剔除。

### 13.4 位运算与技巧

- 与/或/异或/移位：状态位打包、LayerMask、奇偶判断、交换。
- 双缓冲 / 环形缓冲：生产者-消费者、帧缓冲。
- 缓存友好：连续内存遍历 > 指针跳跃。

---

## 14. 游戏客户端架构

### 14.1 分层设计

- 表现层（View）：场景、UI、特效、动画。
- 逻辑层（Model/Controller）：玩法、数值、状态机、战斗。
- 数据层：配置表、存档、服务器数据。
- 基础设施：资源管理、事件中心、网络层、音频、日志、SDK。
- 原则：表现与逻辑分离（换皮不改逻辑、逻辑可单测）、单向依赖、接口解耦。

### 14.2 常用模块

- 资源管理：加载/卸载、引用计数、预加载、异步队列。
- UI 框架：UIManager（打开/关闭/层级/缓存）、UI 基类、界面事件、UI 生命周期。
- 事件中心：跨模块通信，防泄漏（自动反注册或对象生命周期管理）。
- 网络层：连接管理、消息收发、序列化、心跳、重连。
- 配置表：Excel → 工具导出二进制/JSON → 运行时加载（含热更）。
- 战斗框架：实体/组件、技能系统、Buff、伤害结算、表现同步。
- 音频：AudioManager、音效池、场景音乐切换。
- 日志与异常上报：分级日志、堆栈收集、崩溃上报（Bugly 等）。
- 多语言：本地化资源 + 文案表。

### 14.3 启动流程

- Splash → 初始化框架（日志/配置/SDK）→ 检查/下载热更 → 登录 → 进入大厅 → 异步加载战斗场景。
- 首帧优化：避免启动时同步加载大资源，分帧初始化、异步加载、进度条反馈。

---

## 15. 常用框架与工具

### 15.1 热更与脚本

- xLua / XLua / toLua：Lua 热更方案。
- HybridCLR（原 huatuo）：IL2CPP C# 热更。
- UniTask：异步/协程替代，性能好、无分配。

### 15.2 网络

- ET（ET Framework）：双端（C# 服务端 + Unity 客户端），基于 Actor 模型。
- Photon / Mirror / FishNet：Unity 联机框架。
- KCP：UDP 可靠传输库；WebSocket：H5/小程序 场景。

### 15.3 UI

- UGUI：官方，通用。
- FairyGUI：编辑器友好、复杂 UI 与动画。
- NGUI：老牌第三方（已少用）。

### 15.4 工具链

- Profiler / Frame Debugger / Memory Profiler：性能分析。
- Asset Bundle Browser：AB 打包调试。
- RenderDoc / Snapdragon Profiler / Mali Offline Compiler：图形调试。
- Addressables：资源管理。
- CI/CD：Jenkins / GitHub Actions 打包、TestFlight / 蒲公英 分发。
- 版本管理：Git 分支规范、LFS 管理大文件。

---

## 16. 高频面试题速查

**Q1：为什么不能 `new` 一个 MonoBehaviour？**
A：MonoBehaviour 必须挂载在 GameObject 上，生命周期由引擎调度；直接 `new` 只会得到普通 C# 对象，不执行 `Awake/Update` 等生命周期，也无法使用引擎组件功能。正确方式：`AddComponent<T>()` 或从预制体 `Instantiate`。

**Q2：`Awake` 和 `Start` 的区别？**
A：`Awake` 在实例创建时立即调用（组件未启用也调用），用于初始化自身；`Start` 在首次 `Update` 前调用（要求启用），用于依赖其他对象的初始化。同一帧先执行所有 `Awake` 再执行所有 `Start`。

**Q3：`Update`、`FixedUpdate`、`LateUpdate` 分别什么时候用？**
A：`FixedUpdate` 固定步长处理物理；`Update` 每帧处理游戏逻辑与输入；`LateUpdate` 在 `Update` 后调用，适合相机跟随。物理相关移动放 `FixedUpdate`，移动刚体用 `velocity`/`MovePosition`。

**Q4：协程和线程的区别？**
A：协程是单线程的协作式调度（迭代器 + 每帧 `MoveNext`），在 Unity 主线程运行，不能并行、不能做耗时计算；线程真并行，但 Unity API 大多只能在主线程调用，需注意线程安全。

**Q5：`OnTriggerEnter` 和 `OnCollisionEnter` 的触发条件？**
A：双方都要有 Collider，至少一方有 Rigidbody；勾选 `IsTrigger` 走 Trigger 事件（无物理阻挡），否则走 Collision 事件。

**Q6：什么是 Draw Call？如何优化？**
A：CPU 向 GPU 提交的绘制命令次数，过多会卡 CPU。优化：静态合批、动态合批、GPU Instancing、SRP Batcher、图集、LOD、视锥/遮挡剔除、减少 Shader 切换。

**Q7：AssetBundle 如何避免内存泄漏？**
A：统一资源管理器 + 引用计数；加载依赖包；不用时递减计数并在为 0 时 `Unload`；`Unload(false)` 保留已加载资源、`Unload(true)` 全部卸载（慎用）。Addressables 可自动管理。

**Q8：如何降低 GC？**
A：避免装箱、字符串拼接、`Update` 中 `new` 临时对象与 LINQ 闭包；对象池复用；缓存 `WaitForSeconds` 与组件引用；用 `NonAlloc` 物理查询；用 Profiler 定位分配热点。

**Q9：帧同步如何保证确定性？**
A：逻辑与表现分离；浮点运算统一（定点数）；统一随机种子；输入指令序列一致；集合/迭代顺序固定；不使用 `Time.deltaTime` 等帧率相关量做逻辑。

**Q10：移动端性能瓶颈通常在哪？**
A：Overdraw/填充率、纹理带宽与内存（压缩格式）、托管堆 GC、CPU 脚本、Draw Call/合批失败、Shader 复杂度、热更代码解释执行开销。用真机 Profiler 定位。

**Q11：UI 卡顿的原因与优化？**
A：Canvas 重建频繁（改文本/颜色/位置）、合批被打断、Mask 过多、Overdraw、文本过多。优化：动静分离 Canvas、TMP 文本、图集、关闭无用 `RaycastTarget`、RectMask2D、CanvasGroup 淡入淡出。

**Q12：如何计算纹理内存？**
A：宽 x 高 x 每像素字节；RGBA32 为 4 字节，ETC2/ASTC 4x4 约 1 字节/像素；开启 Mipmap 总内存约为基准的 1.33 倍。

**Q13：热更新的原理？**
A：资源用 AssetBundle + 版本清单增量下载；逻辑用 Lua（xLua）或 C# 热更（HybridCLR/ILRuntime）；启动时检查版本 → 下载 → 加载新资源/代码。

**Q14：`ZTest` 和 `ZWrite` 的作用？**
A：`ZTest` 控制片元通过深度测试的条件（默认 `LEqual`）；`ZWrite` 控制是否写入深度缓冲。透明物体一般关 `ZWrite`，避免遮挡后续透明物体。

**Q15：为什么透明物体最后渲染且从远到近排序？**
A：透明度混合依赖像素颜色累加顺序，必须先渲染远处再近处；不透明物体由深度测试决定可见性，无需排序。

**Q16：`Destroy` 和 `DestroyImmediate` 的区别？**
A：`Destroy` 延迟到当前帧末执行，安全；`DestroyImmediate` 立即销毁，可能破坏渲染顺序，仅编辑器/特定场景使用。

**Q17：对象池的原理与注意事项？**
A：预创建/复用对象，避免频繁 `Instantiate/Destroy`。注意：容量上限、状态重置、`OnEnable/OnDisable` 生命周期、隐藏对象不参与渲染。

**Q18：`Time.timeScale` 影响什么？**
A：影响 `Time.deltaTime`、`FixedUpdate` 频率、`WaitForSeconds` 等缩放时间相关逻辑；不影响 `WaitForSecondsRealtime`、`Update` 本身（仍每帧调用）。

**Q19：Mono 和 IL2CPP 的区别？**
A：Mono 为 JIT/解释执行，启动快、调试好、包体小，iOS 受限；IL2CPP 将 IL 转 C++ 编译为原生，性能稳、包体大、构建慢，移动端默认。

**Q20：如何做资源卸载与场景切换优化？**
A：卸载当前场景独有资源（AB `Unload`、`Resources.UnloadUnusedAssets`）、异步加载下个场景、对象池复用、加载进度反馈；用内存快照对比泄漏。
*** End Patch
