## Table of Contents

Introduction 1.1  
出版者的忠告 1.2  
致谢 1.3  
简介 1.4  
第一章 类型推导 1.5  
条款1：理解模板类型推导 1.5.1  
条款2：理解auto类型推导 1.5.2  
条款3：理解decltype 1.5.3  
条款4：知道如何查看类型推导 1.5.4  
第二章 auto关键字 1.6  
条款5：优先使用auto而非显式类型声明 1.6.1  
条款6：当auto推导出非预期类型时应当使用显式的类型初始化 1.6.2  
第三章 使用现代C++ 1.7  
条款7：创建对象时区分()和{} 1.7.1  
条款8：优先使用nullptr而不是0或者NULL 1.7.2  
条款9：优先使用声明别名而不是typedef 1.7.3  
条款10：优先使用作用域限制的enmu而不是无作用域的enum 1.7.4  
条款11：优先使用delete关键字删除函数而不是private却又不实现的函数 1.7.5  
条款12：使用override关键字声明覆盖的函数 1.7.6  
条款13：优先使用const_iterator而不是iterator 1.7.7  
条款14：使用noexcept修饰不想抛出异常的函数 1.7.8  
条款15：尽可能的使用constexpr 1.7.9  
条款16：保证const成员函数线程安全 1.7.10  
条款17：理解特殊成员函数的生成 1.7.11  
第四章 智能指针 1.8  
条款18：使用std::unique_ptr管理独占资源 1.8.1  
条款19：使用std::shared_ptr管理共享资源 1.8.2  
条款20：在std::shared_ptr类似指针可以悬挂时使用std::weak_ptr 1.8.3  
1.8.4 条款21：优先使用std::make_unique和std::make_shared而不是直接使用new  
条款22：当使用Pimpl的时候在实现文件中定义特殊的成员函数 1.8.5  
第五章 右值引用、移动语义和完美转发 1.9  
条款23：理解std::move和std::forward 1.9.1  
条款24：区分通用引用和右值引用 1.9.2  
条款25：在右值引用上使用std::move 在通用引用上使用std::forward 1.9.3  
条款26：避免在通用引用上重定义函数 1.9.4  
条款27：熟悉通用引用上重定义函数的其他选择 1.9.5  
条款28：理解引用折叠 1.9.6  
条款29：假定移动操作不存在，不廉价，不使用 1.9.7  
条款30：熟悉完美转发和失败的情况 1.9.8  
第六章 Lambda表达式 1.10  
条款31：避免默认的参数捕捉 1.10.1  
条款32：使用init捕捉来移动对象到闭包 1.10.2  
条款33：在auto&&参数上使用decltype当std::forward auto&&参数 1.10.3  
条款34：优先使用lambda而不是std::bind 1.10.4  
第七章 并发API 1.11  
条款35：优先使用task-based而不是thread-based 1.11.1  
条款36：当异步是必要的时声明std::launch::async 1.11.2  
条款37：使得std::thread在所有的路径下无法join 1.11.3  
条款38：注意线程句柄析构的行为 1.11.4  
条款39：考虑在一次性事件通信上void的特性 1.11.5  
条款40：在并发时使用std::atomic 在特殊内存上使用volatile 1.11.6  
第八章 改进 1.12  
条款41：考虑对拷贝参数按值传递移动廉价，那就尽量拷贝 1.12.1  
条款42：考虑使用emplace代替insert 1.12.2

# Effective Modern C++

42 SPECIFIC WAYS TO IMPROVE YOUR USE OF C++11 AND C++14

Effective Modern C++ 中文翻译，欢迎大家提出翻译中的错误和用词不当的地方。

<!-- image-->

Scott Meyers

## 代码使用说明

使用gitbook作为静态编译输出，需要安装 Node.js ，然后从 npm 安装gitbook

```batch
npm install gitbook -g
```

然后git clone下来本书，然后输出静态网页，在浏览器上查看：

git clone git@github.com:XimingCheng/Effective-Modern-Cpp-Zh.git   
cd Effective-Modern-Cpp-Zh   
gitbook serve

gitbook会默认在端口 4000 开启服务器，使用浏览器访问http://localhost:4000/就可以访问然后阅读本书的中文翻译。随后我会将本书编译生成的静态网页上传至github pages。

## 出版者的忠告新的，有示例代码

## 使用代码示例

这本书可以让你的工作得心应手。一般来说，如果在本书中提供了示例代码，你可以在你的程序和文档中。你不必为了代码的权限而联系我们，除非你要重新造一个伟大的轮子。举个例子，从书中代码编写一系列代码片段不需要授权，但是贩卖和分发O’Reilly的书籍代码的CD-ROM是需要授权的。引用本书和本书的例子代码来回答一些问题是不需要授权的，但是把很多的书中的代码整合进入你的产品文档里面是需要授权的。

我们会很高兴，但不是强迫引用归属。一个常见的写法包括标题，作者，出版社和ISBN号。举个例子：“Effective	Modern	C++	by	Scott	Meyers	(O’Reilly).	Copyright	2015	Scott	Meyers,978-1-491-90399-5.”

如果你觉得你对本书中的示例代码的使用超出了上述的权利要求范围，欢迎通过permissions@oreilly.com联系我们

## Safari®	Books	Online

Safari	Books	Online是一个应需求的分发世界级领先的技术和商业作家的书籍和视频内容的电子库。

技术专家，软件开发者，web设计师和商务与创新型人士使用Safari	Books	Online作为他们的主力资源进行科研，解决问题，学习和认证训练。

Safari	Books	Online为企业用户，政府部门，教育用户和个人提供一些列的计划和打折

Bartlett，Course	Technology和成百更多这样的可查询的数据库中的千本书籍，训练视频和重新出版的原稿。想获得更多关于Safari	Books	Online的信息，请访问我们的网站。

## 如何联系我们

关于本书的评论和问题可以联系出版社：

O’Reilly Media, Inc. 1005 Gravenstein Highway North Sebastopol, CA 95472 800-998- 9938 (in the United States or Canada) 707-829-0515 (international or local) 707-829- 0104 (fax)

想问关于本书的技术性问题，可以发送邮件到 bookquestions@oreilly.com

想获得更多的关于本书的信息，课程，会议和新闻，参考我们的网站http://www.oreilly.com/

Facebook：http://facebook.com/oreilly

Twitter：http://twitter.com/oreillymedia

YouTube：http://www.youtube.com/oreillymedia

## 致谢

我在2009年开始着力于众所周知的C++0x（现在叫做C++11）。我给Usenet newsgroupcomp.std.c++ 投递了一些问题，我非常感谢社区的成员（特别是Daniel Krügler）的帖子。最近几年，当我有关于C++11和C++14的问题时候，我转战Stack Overflow，我同样受惠于这个社区带给我关于现代C++编程的一些理解。

2010年，我准备了一个关于C++0x的训练课程（最终以Overview of the New C++一书出版）。包括那些材料和知识都归功于和Stephan T. Lavavej, Bernhard Merkle, StanleyFriesen, Leor Zolman, Hendrik Schober, and Anthony Williams的审阅。没有他们的帮助，我可能永远都不会搞出这本Effective Modern C++。这个标题来源于我的一些读者在2014年2月18日发布的blog回帖“Help me name my book”，Andrei Alexandrescu（Modern C++ Design的作者）祝福书的标题不要抄袭他的术语。

我没法确定出这本书的所有原始信息，但是相关的资源有着直接的影响。条款4使用了一个由Stephan T. Lavavej和Matt P. Dziubinski建议在编译器中 coax 类型信息的未定义的模板，这也使得我对Boost.TypeIndex加以关注。在条款5中， unsignedstd::vector<int>::size_type 的例子取自于2010年2月28日Andrey Karpov的文章“In what waycan C++0x standard help you eliminate 64-bit errors”。 std::pair<std::string,int>/std::pair<const std::string, int> 的例子取自于Stephan T. Lavavej在Going Native2012的talk“STL11: Magic && Secrets”。条款6有感于Herb Sutter在2013年8月12日的文章“GotW #94 Solution: AAA Style (Almost Always Auto)”。条款9的灵感来源于2012年5月27号Martinho Fernandes的博客“Handling dependent names”。条款12的检查referencequalifiers的重定义是基于2014年1月14号Casey在Stack Overflow的这个问题“What’s a usecase for overloading member functions on reference qualifiers”的回答。我的条款15的关于C++14对 constexpr 函数的扩展支持的信息来源于Rein Halbersma。条款16是基于HerbSutter的C++ and Beyond 2012的演讲，“You don’t know const and mutable ”。条款18的建议工厂方法返回 std::unique_ptr 是基于Herb Sutter在2013年5月30号的文章，“GotW# 90Solution: Factories”。在条款19中， fastLoadWidget 继承于Herb Sutter的Going Native 2013的演讲，“My Favorite C++ 10-Liner”。我在条款22中关于 std::unique_ptr 的不完备类型的论断来自于Herb Sutter在2011年11月27号的文章，“GotW #100: Compilation Firewalls”和Howard Hinnant在2011年5月22号在Stack Overflow的“Is std::unique_ptr required to knowthe full definition of T?”的回答。在条款25中的矩阵加法运算的例子是基于David Abrahams的作品。JoeArgonne在2012年12月8日的对2012年11月30日发布的帖子“Another alternative tolambda move capture”的评论是条款32的在C++11中基于 std::bind 的模拟init捕捉的来源。条款37的在 std::thread 的析构函数的隐式detach是取自于Hans-J. Boehm的2008年12月4日的paper，“N2802: A plea to reconsider detach-on-destruction for thread objects”。条款41最开始是来源于David Abrahams在2009年8月15日的博客帖子的讨论，“Want speed? Pass byvalue”。关于只移动types deserve special treatment归功于Matthew Fioravante，关于基于赋值的copying stems来源于Howard Hinnant的评论。在条款42中，Stephan T. Lavavej和Howard Hinnant帮助我理解了emplacement和insertion函数的性能区别，Michael Winterberg带给我关于emplacement怎么导致内存泄露的问题，（Michael使用了Sean Parent的GoingNative 2013的演讲，“C++ Seasoning”作为应用来源）。Michael并且指出了emplacement函数是怎么使用直接初始化，而insertion函数是使用拷贝初始化。

对一本技术书籍的校审是一件需要耗费时间精力并且绝对重要的任务，我非常荣幸有这么多的人愿意做这些事情。关于Effective Modern C++全部的或者部分的校审来自于Cassio Neri,Nate Kohl, Gerhard Kreuzer, Leor Zolman, Bart Vandewoestyne, Stephan T. Lavavej, Nevin“:-)” Liber, Rachel Cheng, Rob Stewart, Bob Steagall, Damien Watkins, Bradley E.Needham, Rainer Grimm, Fredrik Winkler, Jonathan Wakely, Herb Sutter, AndreiAlexandrescu, Eric Niebler, Thomas Becker, Roger Orr, Anthony Williams, MichaelWinterberg, Benjamin Huchley, Tom Kirby-Green, Alexey A Nikitin, William Dealtry, HubertMatthews, and Tomasz Kamiński。并且我收到了一些读者通过O’Reilly’s Early ReleaseEBooks和Safari Books Online’s Rough Cuts和我的博客（The View from Aristeia）和电子邮件的反馈。我对这些人非常的感激。这本书有了他们的帮助而变的更好。我要特别感谢Stephan T. Lavavej和Rob Stewart，他们非常非常详细的标注让我怀疑他们在这本书上花的时间比我还多。对Leor Zolman也表示特殊的感谢，他不仅阅读了原稿，还对书中的所有示例代码做了double-check。

电子书的校审是Gerhard Kreuzer, Emyr Williams, and Bradley E. Needham做的.

我对书中的代码单行长度的显示限制在64个字母（这是和电子设备，设备方向切换和字体设置有关系的）是基于Michael Maher的提供。

Ashley Morgan Williams在Lake Oswego Pizzicato uniquely entertaining做好吃的晚餐（老子饿了，为了翻译没吃饭——译者注）。When it comes to man-sized Caesars, she’s the go-togal.（我实在不知道这句是啥意思——译者注）

More than 20 years after first living through my playing author, my wife, Nancy L.Urbano, once again tolerated many months of distracted conversations with a cocktail of resignation, exasperation, and timely splashes of understanding and support. During the same period, our dog, Darla, was largely content to doze away the hours I spent staring at computer screens, but she never let me forget that there’s life beyond the keyboard. （这段描绘了非程 序员的技术型作家的美好生活，和我们的反差太大我已无力翻译——译者注）

## 简介

如果你是一个像我一样有经验的C++程序猿，当初次体验C++11时，“啊，就是他，我明白了，这就是C++”。但是自从你学习了更多的内容，你会惊讶于他的变化。 auto 类型声明，基于区间的 for 循环，lambda表达式和右值引用改变了C++的样貌，还有新的并发API。除此之外，还包括一些合服语言习惯的改动。0和 typedef 都已经过时， nullptr 和别名声明（alias declarations）强势登场。 enum 需要被作用域限制。现在更加建议使用在内部实现的智能指针。移动对象要比拷贝一个对象代价更小。

关于C++11我们要学习很多，还没有提C++14呢。

更重要的是，要想有效的利用好这些特性需要学习很多的东西。如果你拥有了关于“现

代”C++特性，知识储备的基础，但是希望得到一个关于如何正确驾驭这些特性来创造运行正确，高效，可维护和可移植的软件的向导，搜寻的过程是非常具有挑战性的。这就是这本书的目的。他不是来介绍C++11和C++14的新特新的，而是来介绍如何使用他们的高效做法。

这本书的内容被封装成一系列叫做“条款”（item）的东东。想了解更多的关于类型推导的形式吗？或者想知道什么时候用（或者不用） auto 声明吗？你对为什么 const 成员函数必须保证线程安全感兴趣吗？想知道怎么利用 std::unique_ptr 实现Pimpl Idiom，为什么不建议你在lambda表达式里面使用默认的捕捉模式，或者 std::atomic 和 volatile 有什么区别？答案都在这本书里面。更多的是平台独立，标准兼容的答案。这本书讲的是可移植的C++。

书中的条款是指导性建议，并不是法则，因为这些是有意外情况的。重要的不是每条条款带来的建议，而是这些建议背后的道理。一旦你理解了他们，你就可以在你的项目中扮演一个决策者的地位来判断他们是不是违背某个条款的指导性。这本书的目的不是告诉你什么要做，什么不要做，而是要你对C++11和C++14的基础之上进行深层理解。

## 术语和约定

为了让我们之间互相理解，在一开始我们预定C++的一些术语是很重要的。到目前为止有四份关于C++的官方版本，每一份依据对应ISO标准草案定制的年份来命名：C++98，C++03，C++11和C++14。C++98和C++03只是在技术细节上略有区别，在这本书里面我把它们都称之为C++98。当我提到C++11的时候，指的是C++11和C++14，因为C++14就是一个C++11的超集。当我写到C++14的时候，是特指C++14。当我简单的提到C++的时候，应该指的是所有的语言版本。

简介

<table><tr><td rowspan=1 colspan=1>我的表述</td><td rowspan=1 colspan=1>我所指的语言版本</td></tr><tr><td rowspan=1 colspan=1>C++</td><td rowspan=1 colspan=1>所有的版本</td></tr><tr><td rowspan=1 colspan=1>C++98</td><td rowspan=1 colspan=1>C++98和C++03</td></tr><tr><td rowspan=1 colspan=1>C++11</td><td rowspan=1 colspan=1>C++11和C++14</td></tr><tr><td rowspan=1 colspan=1>C++14</td><td rowspan=1 colspan=1>C++14</td></tr></table>

一般来说，我可能绝大时候说C++对运行效率比较重视（对所有的版本都是对的），但是C++98缺乏对并发的支持（这个对于C++03和C++98是对的），但是C++11支持lambda表达式（对C++11和C++14是对的），C++14提供了通用的函数返回值类型推导（对C++14是对的）。

C++11的最普遍的特性是移动语义（move semantics），移动语义的基石是从那些左值中区分出右值。这是因为右值标志着对象是可以在移动操作中使用的而左值通常不是。在概念上来说（在实际中不一定），右值代表着你可以引用的临时对象，不管是通过变量名还是通过一个指针或者左值引用。

一个有用的，有启发意义的判断一个表达式是左值的方法是取它的地址。如果可以取地址，它基本上就是一个左值。如果不行，通常来说是一个右值。这个启发式的特性可以很好的帮助我们记住一个表达式的类型，不管他是一个左值还是一个右值。也就是说，给定一个类型 T ，你可以得到类型 T 的左值同时也可以得到它的右值。当处理一个有右值引用的参数时需要铭记于心，因为参数本身是个左值：

```javascript
class Widget {
public：
Widget(Widget&& rhs); // rhs是一个左值，尽管他
… // 有一个右值引用类型
};
```

这里，在 Widget 的移动构造函数里面完全可以取得 rds 的地址，所以 rds 是一个左值尽管他的类型是个右值引用。（因为类似的原因，所有的参数都是左值。）

这段代码片段阐述了我一般要遵守的几条原则：

类名是 Widget 。我通常会使用 Widget 来代指一个任意的用户自定义类型。我使用 Widget 是不会声明他的，除非我要展示类的特殊细节。

我使用的参数名字叫做 rhs （“right-hand side”）。他是我在移动操作（移动构造函数和移动赋值运算符）中和拷贝操作（拷贝构造函数和复制赋值运算符）喜欢使用的名字。我还把他用在二元运算符的右边的参数：

Matrix operator+(const Matrix& lhs, const Matrix& rhs);

不要惊讶，我希望 lhs 代表“left-hand side”。

我在代码和注释中使用这种格式向你表示你要注意这些东西。在 Widget 的移动构造函数中，我高亮了 rhs 和部分注释来表明 rhs 是一个左值。（很抱歉，译者使用的Markdown语法暂时无法控制代码里面的高亮——译者注。）高亮代码从根本上说不好也不坏。他只是一段你需要加以注意的特殊的代码。

我使用“…”来表示“在此处有其他的代码”。这种比较窄的省略号和用在C++11源代码里面的的变长模板的宽省略号（“...”）是不一样的。这听起来比较困惑。举个例子：

template<typename... Ts> // 这里是C++  
void processVals(const Ts&... params) // 源代码里面的  
{ // 省略号  
… // 此处意味着  
} // “有些代码着这里省略了”

processVals 展示了我在模板中使用 typename 关键字，但是这只是一个个人习惯；关键字 class 也可以工作的正常（这里是不严谨的，nested dependent type name使用的时候， typename 是不能替换成 class 的——译者注）。当我要使用C++标准展示代码，我会使用 class 来做参数类型类型声明，因为标准就是这样做的。

当一个对象使用另外一个类型相同的对象来初始化的时候，新的对象称作一份初始化对象的拷贝，甚至这个拷贝是基于移动构造函数实现的也叫做对象的拷贝。遗憾的是，在C++中没有一个术语是用来区分拷贝构造个移动构造的拷贝。

```cpp
void someFunc(Widget w); // someFunc的参数w是以值传送
Widget wid; // wid是个Widget的对象
someFunc(wid); // 在这个someFunc调用里面，w是通过
// 拷贝构造函数生成wid的一个拷贝
someFunc(std::move(wid)); // 在这个someFunc调用里面，w是通过
// 移动构造函数生成wid的一个拷贝
```

在一个函数调用里面，在函数的调用方的表达式是函数的实参。这些表达式被用来初始化函数的形参。在上面的代码中的第一次调用 someFunc ，实参是 wid 。在第二次调用的地方，实参是 std::move(wid) 。两次调用的形参都是 w 。实参和形参的区别是很重要的，因为形参只能是左值，但是给他们初始化的实参即有可能是右值也有可能是左值。这和完美转发的过程是密切相关的，在完美转发中一个传递给一个函数的实参再传递给第二个函数，以此来保证原始的参数的右值特性或者左值特性被保留。（完美转发的细节在条款30中）。

良好设计的函数是异常安全的，也就意味着他们至少接受基本的异常保证（弱保证）。这样的函数确保调用者触发异常，程序任然保持正常（没有数据结构被损坏）没有资源泄露。函数保证强壮的异常安全（强保证）会确保程序发生异常的时候，程序的运行状态和之前调用这个函数的状态是一样的。

当我提到函数对象（仿函数也属于其中一种——译者注）的时候，我通常意味着这个类型支持 operator() 操作。也就是说，这个对象的行为像一个函数。有时候我会在一些更加通用的地方来使用这种说法（“ functionName(arguments) ”）。更加广义的定义不仅仅包含那些支持 operator() 的对象，也包括函数和C风格的函数指针。（狭义的定义来自于C++98，广义的定义来自于C++11）。添加成员函数指针被称之为可调用对象（callable objects）。通常你可以忽略他们的区别，仅仅认识到在C++中函数对象和可调用对象可以被用在一些函数调用的语法结构里面。

通过lambda表达式创造的函数对象通常称之为闭包（closure）。通常很少区分lambda表达式和它产生的闭包，我通常用lambdas来代指它们。类似的，我很少区分函数模板（生成函数的模板）和模板函数（利用函数模板生成的函数）。对于类模板和模板类也是如此。

在C++许多东西可以声明和定义。声明把类型和名字带入我们的视野但是细节啥都不给，例如是在哪儿放置的存储空间，问题是怎么实现的之类的：

extern int x; // 对象声明  
class Widgets; // class声明  
bool func(const Widget& w); // 函数声明  
enum class Color; // 被作用域包裹的enum声明（参考条款10）

定义提供存储地址或者实现的细节：

```cpp
int x; // 对象定义
class Widget {
… // class定义
};
bool func(const Widget& w)
{ return w.size() < 10; } // 函数定义
enum class Color
{ Yellow, Red, Blue }; // 被作用域包裹的enum定义
```

一个定义当然是需要对应一个声明，除非定义对某个东西非常重要，我通常指的是声明。

我指一个函数的签名是由函数的参数和返回值确定的。函数和参数的名字并不是函数签名的一部分。在上述代码中， func 的签名是 bool(const Widget&) 。函数声明的组成部分除了他的参数和返回值（比如如果有 noexcept 或者 constexpr ）都被排除在外。

（ noexcept 和 constexpr 在条款14和条款15中被讨论）。正式的“签名”的定义和我的略有出入。但对于这本书来说，我的定义会非常有用。（正式的定义会排除返回值类型）。

新的C++标准通常兼容于老的代码，但是有的时候标准化委员会会废弃一些特性。这些特性很有可能在未来的标准化进程中被移除。编译器可能对这些即将废弃的特性没有任何警告，但是你最好要避免使用它们。不仅仅是因为他们会给将来的代码带来头痛，而且他们通常是有好的实现来代替它们。举个例子， std::auto_ptr 被C++11所废弃，因为有更好的相同功能的 std::unique_ptr ，而且能做的更好。（ std::auto_ptr 本来是设计用来防止内存泄露的智能指针，但是为了使用它你必须要注意一堆坑，一般旧的C++书籍也会说明不建议使用——译者注）。

有些时候标准说某个操作会导致未定义行为，这意味着运行时的行为无法预测，不用说，你是需要避开这种不确定性的。一个未确定性的例子是使用方括号（“[]”）去索引超出 std::vector 的长度，从一个未初始化的迭代器取值，或者是有趣的数据竞争（两个或者更多的线程，至少有一个是生产者，同时访问同一块内存区域）。

我把直接从new返回的原始指针叫做内建指针。一个原始指针的反义词就是智能指针。智能指针通常重载了指针取值运算符（ operator-> 和 operator\* ），在条款20里面会解释 std::weak_ptr 是个特殊情况。

在源码注释里面，我通常把“构造函数”简称为ctor，“析构函数”简称为dtor。

## 报告Bug和建议优化

我尽我的努力去让这本书能够带来清楚，准确，有用的信息，但是总是可以再度改善完美的。如果你发现书中的任何错误（技术的，解释的，语法的，印刷的，等等）或者你有一些关于让这本书更好的建议，可以给我发邮件 emc++@aristeia.com。关于修订EffectiveModern C++可以交付于书新版，但是我不能确定出我不知道的问题。

查看这本书已经发现的问题，审核本书的勘误。http://www.aristeia.com/BookErrata/emc++-errata.html。

## 第一章 类型推导

C++98只有一种类型推导规则：函数模板。C++11修改了一点规则样本，并且添加额外的两条规则，一条是 auto ，另一个是 decltype 。C++14继续扩展了 auto 和 decltype 的使用情况。随着类型推导的广泛使用，会使得你从一些明显的或者是冗余的类型拼写中解放出来。它使得C++编写的软件更加具有适用性，因为改变代码中的一处地方的类型，编译器会在代码的其他地方自动的推导出类型定义。但是这使得代码扫描过程更加困难，因为类型推导对编译器来说并不是你想的那么简单。

不去理解类型推导是如何操作的，高效的使用现代C++进行编程是不可能的。在类型推导过程中有太多的上下文判断，在大多数情况， auto 出现在调用函数模板时，在 decltype 表达式里面，和在C++14中，神秘的 decltype(auto) 构造。

本章提供每个C++开发者必需的关于类型推导的信息。解释了模板类型推导是怎么工作的， auto 如何左右类型， decltype 是怎样运行的。甚至解释了如何强制编译器限定显示类型推导的结果，这样会帮助你明确编译器推导的类型是不是你所需要的。

## 条款1：理解模板类型推导

## Understand template type deduction.

当一个复杂系统的用户忽略这个系统是如何工作的，那就再好不过了，因为“如何”扯了一堆系统的设计细节。从这个方面来度量，C++的模板类型推导是个巨大的成功。成百上万的程序猿给模板函数传递完全类型匹配的参数，尽管有很多的程序猿会更加苛刻的给于这个函数推导的类型的严格描述。

如果上面的描述包括你，那我有好消息也有坏消息。好消息就是模板的类型推导是现代C++的最引人注目的特性： auto 。如果你喜欢C++98模板的类型推导，那么你会喜欢上C++11的 auto 对应的模板类型推导。坏消息就是模板类型推导的法则是受限于 auto 的上下文的，有时候看起来应用到模板上不是那么直观。因为这个原因，真正的理解模板 auto 的类型推导是很重要的。这条条款囊括了你的所需。

如果你想大致看一段伪码，一段函数模板看起来会是这样：

```c
template<typename T>
void f(ParamType param);
```

调用会是这样：

```javascript
f(expr);
```

// 用一些表达式来调用f

在编译的时候，编译器通过 expr 来进行推导出两个类型：一个是 T 的，另一个是 ParamType 。通常来说这些类型是不同的，因为 ParamType 通常包含一些类型的装饰，比如 const 或引用特性。举个例子，模板通常采用如下声明：

```cpp
template<typename T>
void f(const T& param); // ParamType 是 const T&
```

如果有这样的调用：

T 被推导成 int ， ParamType 被推导成 const int& 。 。

一般会很自然的期望 T 的类型和传递给他的参数的类型一致，也就是说 T 的类型就是 expr 的类型。在上面的例子中， x 是一个 int ， T 也就被推导成 int 。但是并不是所有的情况都是如此。 T 的类型不仅和 expr 的类型独立，而且还和 ParamType 的形式独立。下面是三个例子：

ParamType 是一个指针或者是一个引用类型，但并不是一个通用的引用类型（通用的引用类型的内容在条款24。此时，你要知道例外情况会出现的，他们的类型并不和左值应用或者右值引用）。

ParamType 是一个通用的引用

ParamType 既不是指针也不是引用

这样的话，我们就有了三种类型需要检查的类型推导场景。每一种都是基于我们队模板的通用的调用封装：

```c
template<typename T>
void f(ParamType param);
f(expr);
```

// 从expr推导出T和ParamType的类型

## 第一种情况： ParamType 是个非通用的引用或者是一个指针

最简单的情况是当 ParamType 是一个引用类型或者是一个指针，但并非是通用的引用。在这种情况下，类型推导的过程如下：

1. 如果 expr 的类型是个引用，忽略引用的部分。

2. 然后利用 expr 的类型和 ParamType 对比去判断 T 的类型。

举一个例子，如果这个是我们的模板，

template<typename T>   
void f(T& param);

我们有这样的代码变量声明：

int x = 27;   
const int cx = x;   
const int& rx = x;

```typescript
// x是一个int
// cx是一个const int
// rx是const int的引用
```

param 和 T 在不同的调用下面的类型推导如下：

f(x); // T是int，param的类型时int&  
f(cx); // T是const int，  
// param的类型是const int&  
f(rx); // T是const int  
// param的类型时const int&

在第二和第三部分的调用，注意 cx 和 rx 由于被指定为 const 类型变量， T 被推导成 constint ，这也就导致了参数的类型被推导为 const int& 。这对调用者非常重要。当传递一个 const 对象给一个引用参数，他们期望对象会保留常量特性，也就是说，参数变成了 const 的引用。这也就是为什么给一个以 T& 为参数的模板传递一个 const 对象是安全的：对象的 const 特性是 T 类型推导的一部分。

在第三个例子中，注意尽管 rx 的类型是一个引用， T 仍然被推导成了一个非引用的。这是因为 rx 的引用特性会被类型推导所忽略。

这些例子展示了左值引用参数的处理方式，但是类型推导在右值引用上也是如此。当然，右值参数只可能传递给右值引用参数，但是这个限制和类型推导没有关系。

如果我们把 f 的参数类型从 T& 变成 const T& ，情况就会发生变化，但是并不会令人惊讶。由于 param 的声明是 const 引用的， cx 和 rx 的 const 特性会被保留，这样的话 T 的 const 特性就没有必要了。

```cpp
template<typename T>
void f(const T& param); // param现在是const的引用
int x = 27; // 和之前一样
const int cx = x; // 和之前一样
const int& rx = x; // 和之前一样
f(x); // T是int，param的类型是const int&
f(cx); // T是int，param的类型是const int&
f(rx); // T是int，param的类型是const int&
```

和之前一样， rx 的引用特性在类型推导的过程中会被忽略。

如果 param 是一个指针（或者指向 const 的指针）而不是引用，情况也是类似：

```c
template<typename T>
void f(T* param); // param是一个指针
int x = 27; // 和之前一样
const int *px = &x; // px是一个指向const int x的指针
f(&x); // T是int，param的类型是int*
f(px); // T是const int
// param的类型时const int*
```

到目前为止，你或许瞌睡了，因为C++在引用和指针上的类型推导法则是如此的自然，我写出来读者看显得很没意思。所有的事情都这么明显！这就是读者所期望的的类型推导系统吧。

## 第二种情况： ParamType 是个通用的引用（UniversalReference）

对于通用的引用参数，情况就变得不是那么明显了。这些参数被声明成右值引用（也就是函数模板使用一个类型参数 T ，一个通用的引用参数的申明类型是 T&& ），但是当传递进去右值参数情况变得不一样。完整的讨论请参考条款24，这里是先行版本。

如果 expr 是一个左值， T 和 ParamType 都会被推导成左值引用。这有些不同寻常。第一，这是模板类型 T 被推导成一个引用的唯一情况。第二，尽管 ParamType 利用右值引用的语法来进行推导，但是他最终推导出来的类型是左值引用。

如果 expr 是一个右值，那么就执行“普通”的法则（第一种情况）

举个例子：

```c
template<typename T>
void f(T&& param); // param现在是一个通用的引用
int x = 27; // 和之前一样
const int cx = x; // 和之前一样
const int& rx = x; // 和之前一样
f(x); // x是左值，所以T是int&
// param的类型也是int&
f(cx); // cx是左值，所以T是const int&
// param的类型也是const int&
f(rx); // rx是左值，所以T是const int&
// param的类型也是const int&
f(27); // 27是右值，所以T是int
// 所以param的类型是int&&
```

条款23解释了这个例子推导的原因。关键的地方在于通用引用的类型推导法则和左值引用或者右值引用的法则大不相同。特殊的情况下，当使用了通用的引用，左值参数和右值参数的类型推导大不相同。这在非通用的类型推到上面绝对不会发生。

## 第三种情况： ParamType 既不是指针也不是引用

当 ParamType 既不是指针也不是引用，我们把它处理成pass-by-value：

```c
template<typename T>
void f(T param);
```

// param现在是pass-by-value

这就意味着 param 就是完全传给他的参数的一份拷贝——一个完全新的对象。基于这个事实可以从 expr 给出推导的法则：

1. 和之前一样，如果 expr 的类型是个引用，将会忽略引用的部分。

2. 如果在忽略 expr 的引用特性， expr 是个 const 的，也要忽略掉 const 。如果是 volatile ，照样也要忽略掉（ volatile 对象并不常见。它们常常被用在实现设备驱动上面。查看更多的细节，请参考条款40。）

这样的话：

int x = 27; // 和之前一样  
const int cx = x; // 和之前一样  
const int& rx = x; // 和之前一样  
f(x); // T和param的类型都是int  
f(cx); // T和param的类型也都是int  
f(rx); // T和param的类型还都是int

注意尽管 cx 和 rx 都是 const 类型， param 却不是 const 的。这是有道理的。 param 是一个和 cx 和 rx 独立的对象——一个 cx 和 rx 的拷贝。 cx 和 rx 不能被修改和 param 能不能被修改是没有关系的。这就是为什么 expr 的常量特性（或者是易变性）（在很多的C++书籍上面 const 特性和 volatile 特性被称之为CV特性——译者注）在推导 param 的类型的时候被忽略掉了： expr 不能被修改并不意味着它的一份拷贝不能被修改。

认识到 const （和 volatile ）在按值传递参数的时候会被忽略掉。正如我们所见，引用的 const 或者是指针指向 const ， expr 的 const 特性在类型推导的过程中会被保留。但是考虑到 expr 是一个 const 的指针指向一个 const 对象，而且 expr 被通过按值传递传递给 param ：

```c
template<typename T>
void f(T param); // param仍然是按值传递的（pass by value）
const char* const ptr = // ptr是一个const指针，指向一个const对象
"Fun with pointers";
f(ptr); // 给参数传递的是一个const char * const类型
```

这里，位于星号右边的 const 是表明指针是常量 const 的： ptr 不能被修改指向另外一个不同的地址，并且也不能置成 null 。（星号左边的 const 表明 ptr 指向的——字符串—是 const 的，也就是说字符串不能被修改。）当这个 ptr 传递给 f ，组成这个指针的内存bit被拷贝给 param 。这样的话，指针自己（ ptr ）本身是被按值传递的。按照按值传递的类型推导法则， ptr 的 const 特性会被忽略，这样 param 的推导出来的类型就是 const char\* ，也就是一个可以被修改的指针，指向一个 const 的字符串。 ptr 指向的东西的 const 特性被加以保留，但是 ptr 自己本身的 const 特性会被忽略，因为它要被重新复制一份而创建了一个新的指针 param 。 。

## 数组参数

这主要出现在mainstream的模板类型推导里面，但是有一种情况需要特别加以注意。就是数组类型和指针类型是不一样的，尽管它们通常看起来是可以替换的。一个最基本的幻觉就是在很多的情况下，一个数组会被退化成一个指向其第一个元素的指针。这个退化的代码常常如此：

```javascript
const char name[] = "J. P. Briggs"; // name的类型是const char[13]
const char * ptrToName = name; // 数组被退化成指针
```

在这里， const char\* 指针 ptrToName 使用 name 初始化，实际的 name 的类型是 constchar[13] 。这些类型（ const char\* 和 const char[13] ）是不一样的，但是因为数组到指针的退化规则，代码会被正常编译。

但是如果一个数组传递给一个安置传递的模板参数里面情况会如何？会发生什么呢？

template<typename T>  
void f(T param); // 模板拥有一个按值传递的参数  
f(name); // T和param的类型会被推到成什么呢？

我们从一个没有模板参数的函数开始。是的，是的，语法是合法的，但是以数组声明，但是还是把它当成一个指针声明，也就是说 myFunc 可以和下面的声明等价：

void myFunc(int param[]); // 和上面的函数相同

void myFunc(int\* param); // 和上面的函数是一样的

这样的数组和指针等价的声明经常会在以C语言为基础的C++里面出现，这也就导致了数组和指针是等价的错觉。

因为数组参数声明会被当做指针参数，传递给模板函数的按值传递的数组参数会被退化成指针类型。这就意味着在模板 f 的调用中，模板参数 T 被推导成 const char\* ：

```javascript
f(name);
```

```javascript
// name是个数组，但是T被推导成const char*
```

但是来一个特例。尽管函数不能被真正的定义成参数为数组，但是可以声明参数是数组的引用！所以如果我们修改模板 f 的参数成引用，

template<typename T>  
void f(T& param); // 引用参数的模板

然后传一个数组给他

```javascript
f(name);
```

// 传递数组给f

T 最后推导出来的实际的类型就是数组！类型推导包括了数组的长度，所以在这个例子里面， T 被推导成了 const char [13] ，函数 f 的参数（数组的引用）被推导成了 const char(&)[13] 。是的，语法看起来怪怪的，但是理解了这些可以升华你的精神（原文knowing it willscore you mondo points with those few souls who care涉及到了几个宗教词汇——译者注）。

有趣的是，声明数组的引用可以使的创造出一个推导出一个数组包含的元素长度的模板：

```cpp
// 在编译的时候返回数组的长度（数组参数没有名字，
// 因为只关心数组包含的元素的个数）
template<typename T, std::size_t N>
constexpr std::size_t arraySize(T (&)[N]) noexcept
{
return N; // constexpr和noexcept在随后的条款中介绍
}
```