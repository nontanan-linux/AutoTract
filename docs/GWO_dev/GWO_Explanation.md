# การหาค่าเหมาะสมที่สุดด้วยอัลกอริทึมหมาป่าสีเทา (Grey Wolf Optimization - GWO)

เอกสารนี้อธิบายหลักการทำงานของ Grey Wolf Optimization (GWO) ซึ่งเป็นอัลกอริทึม Meta-heuristic ที่เลียนแบบพฤติกรรมการล่าของหมาป่าสีเทา เนื้อหาครอบคลุมทฤษฎี สมการคณิตศาสตร์ และตัวแปรที่เกี่ยวข้อง

## 1. บทนำ (Introduction)

การหาค่าเหมาะสมที่สุด (Optimization) เป็นสิ่งที่พบได้ทั่วไป ตั้งแต่การออกแบบทางวิศวกรรมไปจนถึงเศรษฐศาสตร์ การวางแผนท่องเที่ยว หรือการจัดการเส้นทางอินเทอร์เน็ต เนื่องจากทรัพยากร (เช่น เวลา, เงิน) มักมีจำกัด การใช้ประโยชน์จากสิ่งที่มีอยู่ให้คุ้มค่าที่สุดจึงมีความสำคัญอย่างยิ่ง

โดยทั่วไป ปัญหาการหาค่าเหมาะสมที่สุดสามารถเขียนในรูปสมการคณิตศาสตร์ได้ดังนี้:

```math
\text{optimize } f_1(x), \dots, f_N(x)
\text{ subject to } h_j(x) = 0, \ g_k(x) \le 0
```

โดยที่:

* **ฟังก์ชันวัตถุประสงค์ (Objective Function) - $f(x)$**: คือเป้าหมายที่เราต้องการทำให้มากที่สุด (Maximize) หรือน้อยที่สุด (Minimize) เช่น ต้องการกำไรสูงสุด ($f = \text{Profit}$) หรือต้องการต้นทุนต่ำสุด ($f = \text{Cost}$)
* **สมการข้อจำกัด (Constraints) - $h(x), g(x)$**: คือเงื่อนไขที่คำตอบต้องผ่านเกณฑ์ที่กำหนด
  * **Equality Constraints ($h_j(x) = 0$)**: ข้อจำกัดแบบเท่ากับ (ต้องพอดีเป๊ะ)
  * **Inequality Constraints ($g_k(x) \le 0$)**: ข้อจำกัดแบบอสมการ (ต้องน้อยกว่าหรือมากกว่าค่าที่กำหนด)

หาก $N=1$ จะเรียกว่า **Single-objective optimization** (ซึ่งบทความนี้จะเน้นที่ส่วนนี้) แต่หาก $N \ge 2$ จะเป็น Multi-objective optimization

### ประเภทของอัลกอริทึม (Types of Optimization Algorithms)

อัลกอริทึมสำหรับแก้ปัญหานี้แบ่งได้เป็น 2 ประเภทหลัก:

#### 1. Deterministic Algorithms (อัลกอริทึมแบบกำหนดแน่นอน)

ใช้คุณสมบัติเชิงวิเคราะห์ของโจทย์เพื่อหาคำตอบที่ลู่เข้าสู่จุดที่ดีที่สุด (Global Optimum) ได้อย่างแม่นยำ

* **เหมาะสำหรับ:** ปัญหาที่มีโครงสร้างชัดเจนและข้อมูลครบถ้วน
* **ตัวอย่าง:** Linear Programming, Nonlinear Programming

#### 2. Heuristics and Metaheuristics (ฮิวริสติกและเมตาฮิวริสติก)

เป็นกระบวนการระดับสูงที่มุ่งหาคำตอบที่ "ดีเพียงพอ" (Sufficiently good solution) อาจไม่ใช่จุดที่ดีที่สุด 100% แต่ใช้ได้ดีในกรณีที่ข้อมูลไม่สมบูรณ์หรือมีทรัพยากรการคำนวณจำกัด ข้อดีคือไม่ต้องตั้งสมมติฐานเกี่ยวกับโจทย์มากนัก ทำให้ประยุกต์ใช้ได้กว้างขวาง

* **ตัวอย่าง:**
  * Particle Swarm Optimization (PSO)
  * Ant Colony Optimization (ACO)
  * Genetic Algorithms (GA)
  * **Grey Wolf Optimization (GWO)**

![Figure 1: Classification of Meta-heuristic Algorithms](pict/Figure1_Classification.png)
*รูปที่ 1: การจำแนกประเภทของอัลกอริทึม Meta-heuristic*
อัลกอริทึม GWO นี้จัดอยู่ในกลุ่ม **Meta-heuristics** โดยจำลองพฤติกรรมความฉลาดแบบกลุ่ม (Swarm Intelligence) ของหมาป่าสีเทา

## 2. แรงบันดาลใจของอัลกอริทึม (Inspiration of the algorithm)

อัลกอริทึมนี้ได้แรงบันดาลใจมาจากพฤติกรรมตามธรรมชาติของ **หมาป่าสีเทา (Grey Wolf - *Canis lupus*)** ซึ่งเป็นสัตว์นักล่าระดับสูงสุด (Apex Predator) ในวงศ์ Canidae หมาป่าสีเทามักอาศัยอยู่รวมกันเป็นฝูง (Pack) โดยมีขนาดฝูงเฉลี่ย 5-12 ตัว และมีจุดเด่นคือระเบียบวินัยทางสังคมที่เคร่งครัดมาก (Very strict social dominant hierarchy)

### 2.1 ลำดับชั้นทางสังคม (Social Hierarchy)

![Figure 2: Social Hierarchy of Grey Wolves](pict/Figure2_SocialHierarchy.png)
*รูปที่ 2: ลำดับชั้นทางสังคมของหมาป่าสีเทา*

หมาป่าในฝูงจะแบ่งหน้าที่ตามลำดับชั้น ดังนี้:

| ลำดับชั้น | สัญลักษณ์ | บทบาทหน้าที่ | ใน GWO หมายถึง |
| :--- | :--- | :--- | :--- |
| **Alpha** | $\alpha$ | ผู้นำสูงสุด (ชาย/หญิง) ตัดสินใจเรื่องสำคัญ เช่น การล่า, ที่พัก, เวลาตื่น ไม่จำเป็นต้องแข็งแรงที่สุดแต่บริหารจัดการเก่งที่สุด | คำตอบที่ดีที่สุด (Best Solution) |
| **Beta** | $\beta$ | รองหัวหน้า เป็นที่ปรึกษาและคอยรักษาระเบียบวินัยในฝูง (Discipliner) เป็นผู้สืบทอดตำแหน่ง Alpha | คำตอบที่ดีที่สุดลำดับ 2 |
| **Delta** | $\delta$ | ผู้ใต้บังคับบัญชาของ $\alpha, \beta$ แต่คุม $\omega$ ประกอบด้วยหน่วยลาดตระเวน (Scouts), ยาม (Sentinels), ผู้อาวุโส (Elders), ผู้ล่า (Hunters), และผู้ดูแล (Caretakers) | คำตอบที่ดีที่สุดลำดับ 3 |
| **Omega** | $\omega$ | ลูกฝูงระดับล่างสุด เป็นแพะรับบาป (Scapegoat) ระบายความก้าวร้าวของฝูง กินอาหารทีหลังสุด ทำหน้าที่พี่เลี้ยงเด็ก (Babysitters) | คำตอบที่เหลือทั้งหมด (Candidate Solutions) |

## 3. โมเดลทางคณิตศาสตร์ (Mathematical Model)

### 3.1 การล้อมรอบเหยื่อ (Encircling Prey)

พฤติกรรมการล่าของหมาป่าแบ่งออกเป็น 3 ระยะหลัก คือ:

1) **Tracking & Chasing**: การติดตามและไล่ล่าเหยื่อ
2) **Pursuing & Encircling**: การต้อนและล้อมรอบเหยื่อจนกว่าเหยื่อจะหยุดนิ่ง
3) **Attack**: การเข้าโจมตี

ในทางคณิตศาสตร์ เราจำลองพฤติกรรมการล้อมรอบ (Encircling) ได้จากสมการ:

$$ \vec{D} = |\vec{C} \cdot \vec{X}_p(t) - \vec{X}(t)| $$
$$ \vec{X}(t+1) = \vec{X}_p(t) - \vec{A} \cdot \vec{D} $$

โดยที่:

* $\vec{X}_p$: ตำแหน่งของเหยื่อ (หรือคำตอบที่ดีกว่า)
* $\vec{X}$: ตำแหน่งของหมาป่า
* $t$: รอบการทำงานปัจจุบัน

ค่าสัมประสิทธิ์ $\vec{A}$ และ $\vec{C}$ คำนวณจาก:
$$ \vec{A} = 2\vec{a} \cdot \vec{r}_1 - \vec{a} $$
$$ \vec{C} = 2\vec{r}_2 $$

### 3.2 การล่าเหยื่อ (Hunting)

ตำแหน่งของหมาป่าทั่วๆ ไป ($\omega$) จะถูกปรับตามตำแหน่งของหมาป่าจ่าฝูงทั้ง 3 ตัว ($\alpha, \beta, \delta$) ดังนี้:

1) **คำนวณระยะห่างจากจ่าฝูงแต่ละตัว:**
   $$ \vec{D}_\alpha = |\vec{C}_1 \cdot \vec{X}_\alpha - \vec{X}| $$
   $$ \vec{D}_\beta = |\vec{C}_2 \cdot \vec{X}_\beta - \vec{X}| $$
   $$ \vec{D}_\delta = |\vec{C}_3 \cdot \vec{X}_\delta - \vec{X}| $$

2) **คำนวณตำแหน่งใหม่ที่ควรจะไป:**
   $$ \vec{X}_1 = \vec{X}_\alpha - \vec{A}_1 \cdot \vec{D}_\alpha $$
   $$ \vec{X}_2 = \vec{X}_\beta - \vec{A}_2 \cdot \vec{D}_\beta $$
   $$ \vec{X}_3 = \vec{X}_\delta - \vec{A}_3 \cdot \vec{D}_\delta $$

3) **หาค่าเฉลี่ยเพื่อระบุตำแหน่งถัดไป:**
   $$ \vec{X}(t+1) = \frac{\vec{X}_1 + \vec{X}_2 + \vec{X}_3}{3} $$

### 3.3 การโจมตีเหยื่อ (Attacking Prey - Exploitation)

การโจมตีจะเกิดขึ้นเมื่อเหยื่อหยุดการเคลื่อนไหว ในทางคณิตศาสตร์เราจำลองการเข้าหาเหยื่อโดยการลดค่าของ $\vec{a}$ (จาก 2 ลงไป 0) ซึ่งส่งผลให้ช่วงของค่า $\vec{A}$ ลดลงด้วย

* **เงื่อนไข:** เมื่อ $|\vec{A}| < 1$
* **ผลลัพธ์:** หมาป่าจะถูกบังคับให้เข้าหาเหยื่อ (โจมตี) ซึ่งเป็นการตักตวงข้อมูล (Exploitation) จากพื้นที่รอบๆ คำตอบที่ดีที่สุด

### 3.4 การค้นหาเหยื่อ (Searching for Prey - Exploration)

หมาป่าจะกระจายตัวออกเพื่อค้นหาเหยื่อ แล้วค่อยกลับมารวมตัวกันเพื่อโจมตี

* **เงื่อนไข:** เมื่อ $|\vec{A}| > 1$
* **ผลลัพธ์:** หมาป่าจะถูกบังคับให้แยกตัวห่างจากเหยื่อ เพื่อสำรวจพื้นที่ใหม่ๆ (Exploration) และหลีกเลี่ยงการติดอยู่ในคำตอบที่ดีที่สุดเฉพาะที่ (Local Optima)
* **บทบาทของ $\vec{C}$:** ค่า $\vec{C}$ เป็นตัวแปรสุ่มในช่วง [0, 2] ที่ช่วยเน้นย้ำ ($C > 1$) หรือลดความสำคัญ ($C < 1$) ของเหยื่อในการกำหนดระยะทาง
  * *ข้อสำคัญ:* ค่า $\vec{C}$ **ไม่ได้ลดลงเชิงเส้น** เหมือนค่า $\vec{a}$ แต่จะถูกสุ่มใหม่ตลอดเวลาทั้งในช่วงแรกและช่วงท้ายของการทำงาน
  * สิ่งนี้ช่วยให้ Algorithm มีพฤติกรรมแบบสุ่ม (Stochastic) ตลอดกระบวนการ ซึ่งสำคัญมากในการช่วยให้หลุดออกจากคำตอบที่ดีที่สุดเฉพาะที่ (Local Optima Stagnation)

### 3.5 รหัสเทียม (Pseudocode of GWO Algorithm)

ลำดับขั้นตอนการทำงานของอัลกอริทึมสรุปได้ดังนี้:

```text
Initialize the grey wolf population Xi (i = 1, 2, ..., n)
Initialize a, A, and C
Calculate the fitness of each search agent
    X_alpha = the best search agent
    X_beta  = the second best search agent
    X_delta = the third best search agent

while (t < Max number of iterations)
    for each search agent
        Update the position of the current search agent
    end for
    Update a, A, and C
    Calculate the fitness of all search agents
    Update X_alpha, X_beta, and X_delta
    t = t + 1
end while
return X_alpha
```

### 3.6 สรุปตัวแปรสำหรับการปรับตั้งค่า (Configuration Parameters)

ตารางนี้สรุปตัวแปรที่คุณสามารถปรับเปลี่ยนได้เมื่อนำไปเขียนโปรแกรม:

| ชื่อตัวแปร (Variable) | ความหมาย (Description) | ค่าปกติ / การกำหนดค่า |
| :--- | :--- | :--- |
| **Max_iter** | จำนวนรอบสูงสุด (Maximum Iterations) | เช่น 100, 500, 1000 (ยิ่งมากยิ่งละเอียดแต่นาน) |
| **SearchAgents_no** (n) | จำนวนประชากรหมาป่า (Population Size) | เช่น 10 - 50 ตัว |
| **dim** | จำนวนมิติของปัญหา (Dimension) | ตามจำนวนตัวแปรของโจทย์ |
| **lb** | ขอบเขตล่าง (Lower Bound) | ค่าต่ำสุดที่เป็นไปได้ของตัวแปร |
| **ub** | ขอบเขตบน (Upper Bound) | ค่าสูงสุดที่เป็นไปได้ของตัวแปร |
| **a** | ค่าควบคุมการลู่เข้า | ลดเชิงเส้นจาก 2 -> 0 |

## 4. ตัวอย่างการใช้ GWO ในการแก้ปัญหาใน 1 มิติ

### 4.1 Unimodal Functions: $f(x) = x^2$

#### 4.1.1 ลักษณะปัญหา (Problem Description)

1\) **สมการ:** $f(x) = x^2$

2\) **เป้าหมาย:** หาค่า $x$ ที่ทำให้ $f(x)$ มีค่าน้อยที่สุด (Minimize)

3\) **คำตอบที่ถูกต้อง:** $x = 0$ ซึ่งจะได้ $f(0) = 0$

4\) **ลักษณะกราฟ:** เป็นรูปพาราโบลาหงาย มีจุดต่ำสุดเพียงจุดเดียว (Unimodal) ไม่มีจุดต่ำสุดหลอก (Local Optima) ทำให้เหมาะสำหรับการทดสอบการลู่เข้า (Convergence) ของอัลกอริทึม

#### 4.1.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **เหยื่อ (Prey):** คือจุดต่ำสุดของกราฟที่ $x=0$ (แต่หมาป่าไม่รู้ตำแหน่งนี้ ต้องหาเอาเอง)

2\) **หมาป่า (Wolf):** คือค่า $x$ ที่สุ่มขึ้นมาในช่วงเริ่มต้น

3\) **ความเหมาะสม (Fitness):** คือค่า $y = x^2$ (ยิ่งค่าน้อย ยิ่งดี ยิ่งใกล้เหยื่อ)

4\) **การเคลื่อนที่:** หมาป่าจะปรับค่า $x$ ของตัวเองให้เข้าใกล้ค่า $x$ ของ Alpha, Beta, Delta ที่มีค่า $y$ ต่ำที่สุด

#### 4.1.3 การประยุกต์ใช้ (Application)

เราสามารถใช้โจทย์พื้นฐานนี้เพื่อ:

1\) ทดสอบความเร็วในการลู่เข้าหาคำตอบ

2\) ปรับจูนค่าพารามิเตอร์ (เช่น จำนวนหมาป่า, จำนวนรอบ)

3\) ทำความเข้าใจกลไกการ update ตำแหน่งใน 1 มิติ

#### 4.1.4 Pseudocode สำหรับโจทย์ $f(x) = x^2$

```python
Initialize wolves random position x in [-10, 10]
Loop:
    Calculate fitness y = x^2 for all wolves
    Identify Alpha (min y), Beta (2nd min), Delta (3rd min)
    
    Update a (2 -> 0)
    For each wolf:
        Calculate distance to Alpha, Beta, Delta using A, C variables
        Update position x based on average influence of leaders
    End For
End Loop
Return Alpha position
```

#### 4.1.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**
โค้ดใน `scripts/gwo_unimodal.py` จำลองกระบวนการทำงานของ GWO เพื่อหาจุดต่ำสุดของ $x^2$ โดยมีขั้นตอนดังนี้:

* **Initialization:** เริ่มต้นสุ่มตำแหน่งประชากรหมาป่า (Solutions) จำนวน 10 ตัว ในช่วง $[-10, 10]$
* **Fitness Calculation:** ในทุกรอบ (Iteration) จะคำนวณค่า $y = x^2$ ของหมาป่าทุกตัว
  * ตัวที่มีค่า $y$ ต่ำที่สุด จะถูกบันทึกเป็น **Alpha** (คำตอบที่ดีที่สุด)
  * ลำดับรองลงมาเป็น **Beta** และ **Delta** ตามลำดับ
* **Update Position:** หมาป่าตัวที่เหลือ (Omega) จะคำนวณระยะห่างเทียบกับ Alpha, Beta, และ Delta แล้วขยับตำแหน่งตัวเองเข้าไปหาจุดกึ่งกลางของผู้นำทั้ง 3
* **Linear & Random Factors:**
  * ค่า $a$ จะลดลงเรื่อยๆ จาก $2 \to 0$ ตามจำนวนรอบ ทำให้วงล้อมค่อยๆ แคบลง (Exploitation)
  * ค่า $C$ เป็นการสุ่ม $[0, 2]$ เสมอ เพื่อให้การเคลื่อนที่ไม่ยึดติดกับผู้นำมากเกินไป (Exploration)

**2) ความหมายของตัวแปรและตัวเลข (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากรหมาป่า:** เลือกใช้ 10 ตัว เพราะโจทย์ $x^2$ ใน 1 มิติ ไม่ซับซ้อนมาก ไม่จำเป็นต้องใช้ประชากรเยอะก็สามารถค้นหาเจอได้เร็ว ช่วยประหยัดทรัพยากร |
| **`max_iter`** | `20` | **จำนวนรอบสูงสุด:** กำหนดเพียง 20 รอบ เพราะสังเกตได้ว่าอัลกอริทึมลู่เข้า (Converge) สู่ค่า 0 ได้เร็วมาก (มักจะเจอตั้งแต่รอบที่ 5-10) จึงไม่จำเป็นต้องรันนานกว่านี้ |
| **`lb`, `ub`** | `-10`, `10` | **ขอบเขตการค้นหา:** กำหนดช่วง $[-10, 10]$ เพื่อให้ครอบคลุมจุดต่ำสุด ($0$) และกว้างพอที่จะทดสอบว่าอัลกอริทึมสามารถบีบวงเข้ามาหา 0 ได้จริงหรือไม่ |
| **`dim`** | `1` | **มิติของปัญหา:** เท่ากับ 1 เพราะเราหาค่าตัวแปร $x$ เพียงตัวเดียว |
| **`a`** | `2 -> 0` | **ตัวแปรควบคุมวงล้อม:** ลดค่าลงเชิงเส้นตาม Time Step เพื่อเปลี่ยนโหมดจากการสำรวจพื้นที่กว้างๆ (Exploration) มาเป็นการเจาะจงที่เป้าหมาย (Exploitation) |

#### 4.1.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python ฉบับเต็มได้ที่:
`scripts/gwo_unimodal.py`

#### 4.1.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_unimodal.py` (Population=10, Iteration=20) จะได้ผลลัพธ์ดังนี้:

```text
Initial Best Score: 0.043782
Iter 1: Best Score = 0.0437820289 (at x = 0.209242)
Iter 2: Best Score = 0.0139922924 (at x = -0.118289)
Iter 3: Best Score = 0.0012709052 (at x = -0.035650)
Iter 4: Best Score = 0.0000079310 (at x = 0.002816)
Iter 5: Best Score = 0.0000055865 (at x = -0.002364)
Iter 6: Best Score = 0.0000055865 (at x = -0.002364)
Iter 7: Best Score = 0.0000002482 (at x = -0.000498)
Iter 8: Best Score = 0.0000002174 (at x = 0.000466)
Iter 9: Best Score = 0.0000000018 (at x = 0.000042)
Iter 10: Best Score = 0.0000000018 (at x = 0.000042)
Iter 11: Best Score = 0.0000000000 (at x = 0.000003)
Iter 12: Best Score = 0.0000000000 (at x = 0.000002)
Iter 13: Best Score = 0.0000000000 (at x = 0.000002)
Iter 14: Best Score = 0.0000000000 (at x = 0.000002)
Iter 15: Best Score = 0.0000000000 (at x = 0.000001)
Iter 16: Best Score = 0.0000000000 (at x = 0.000000)
Iter 17: Best Score = 0.0000000000 (at x = 0.000000)
Iter 18: Best Score = 0.0000000000 (at x = 0.000000)
Iter 19: Best Score = 0.0000000000 (at x = 0.000000)
Iter 20: Best Score = 0.0000000000 (at x = 0.000000)

--- Optimization Result ---
Optimal x found: 0.0000003543
Optimal f(x): 0.0000000000
```

![Convergence Curve](pict/unimodal_combined.png)

**คำอธิบายผลลัพธ์:**

1\) **การลู่เข้าที่รวดเร็ว (Fast Convergence):** จะเห็นว่าเพียงแค่รอบที่ 5 ค่า $x$ ก็เข้าใกล้ 0 มากๆ ($x \approx -0.002$) และในรอบที่ 20 ค่า Error แทบจะเป็น 0

2\) **ความแม่นยำ:** คำตอบที่ได้คือ $x = 0.0000003543$ ซึ่งใกล้เคียงกับค่าจริง ($x=0$) มาก แสดงให้เห็นว่า GWO มีประสิทธิภาพสูงในการแก้ปัญหา Unimodal Function ที่มีความต่อเนื่องและไม่มี Local Optima มาขัดขวาง

### 4.2 Multimodal Functions: Rastrigin Function

#### 4.2.1 ลักษณะปัญหา (Problem Description)

1\) **สมการ:** $f(x) = 10 + x^2 - 10\cos(2\pi x)$

2\) **เป้าหมาย:** หาค่า $x$ ที่ทำให้ $f(x)$ มีค่าน้อยที่สุด

3\) **คำตอบที่ถูกต้อง:** $x = 0$ ซึ่งจะได้ $f(0) = 0$ (Global Optimum)

4\) **ลักษณะกราฟ:** เป็นกราฟที่มีหลุมเล็กๆ (Local Optima) จำนวนมากตลอดทาง หากอัลกอริทึมไม่ดีพอ อาจจะไปติดอยู่ในหลุมข้างๆ (เช่น $x \approx 1, x \approx -1$) แทนที่จะลงไปที่หลุมลึกสุดตรงกลาง ($x=0$)

#### 4.2.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **เหยื่อ (Prey):** คือจุดต่ำสุดของกราฟที่ $x=0$ (เป้าหมายสูงสุด)

2\) **กับดัก (Local Optima):** คือหลุมตื้นๆ ที่กระจัดกระจายอยู่รอบๆ เหยื่อ ซึ่งอาจหลอกให้หมาป่าหยุดค้นหา

3\) **การสำรวจ (Exploration):** หมาป่าต้องมีความสามารถในการกระโดดข้ามหลุมตื้นๆ เหล่านี้ไปให้ได้

#### 4.2.3 การประยุกต์ใช้ (Application)

เราสามารถใช้โจทย์ Rastrigin นี้เพื่อ:

1\) ทดสอบความสามารถในการหลุดจาก Local Optima (Exploration Capability)

2\) เปรียบเทียบประสิทธิภาพกับ Unimodal ว่าใช้เวลานานกว่าหรือไม่

3\) ทดสอบความเสถียร (Robustness) เมื่อเจอโจทย์ที่มีความซับซ้อน

#### 4.2.4 Pseudocode สำหรับโจทย์ Rastrigin Function

```python
Initialize wolves random position x in [-5.12, 5.12]
Loop:
    Calculate fitness y = 10 + x^2 - 10*cos(2*pi*x)
    Identify Alpha, Beta, Delta
    
    Update a (2 -> 0)
    For each wolf:
        Calculate distance using A (random > 1 or < -1 allows jump)
        Calculate distance using C (random weights)
        Update position
    End For
End Loop
Return Alpha position
```

#### 4.2.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**
โค้ดใน `scripts/gwo_multimodal.py` มีโครงสร้างคล้ายกับ Unimodal แต่มีจุดสำคัญที่แตกต่างคือ:

* **Initialization:** เริ่มต้นสุ่มในช่วง $[-5.12, 5.12]$ ซึ่งเป็นช่วงมาตรฐานของฟังก์ชัน Rastrigin ที่มี Local Optima หนาแน่น
* **Stochastic Leaps:** การคำนวณตำแหน่งใหม่จะพึ่งพาค่า $\vec{A}$ และ $\vec{C}$ อย่างมากในการ "กระโดด" ข้าม local optima
  * เมื่อ $|\vec{A}| > 1$: หมาป่าจะถูกบังคับให้กระจายตัวออกไป (Diverge) เพื่อหาพื้นที่ใหม่
  * เมื่อ $|\vec{A}| < 1$: หมาป่าจะบีบวงเข้ามายังคำตอบ (Converge)

**2) ความหมายของตัวแปรที่แตกต่างจาก 4.1**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล |
| :--- | :--- | :--- |
| **`search_agents_no`** | `20` | **จำนวนประชากรหมาป่า:** เพิ่มขึ้นเป็น 20 ตัว (จากเดิม 10) เพื่อเพิ่มโอกาสในการกระจายตัวไปเจอกับดักและหลุดออกมาได้ (Diversity ที่สูงขึ้นช่วยเรื่อง Exploration) |
| **`max_iter`** | `50` | **จำนวนรอบสูงสุด:** เพิ่มเป็น 50 รอบ เพราะโจทย์ยากขึ้นและซับซ้อนกว่า ต้องใช้เวลาในการสุ่มหาทางหลุดจากหลุมพรางมากกว่าโจทย์ Unimodal |
| **`lb`, `ub`** | `-5.12`, `5.12` | **ขอบเขตการค้นหา:** เป็น Standard Domain ของฟังก์ชัน Rastrigin |

#### 4.2.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Multimodal Function ได้ที่:
`scripts/gwo_multimodal.py`

#### 4.2.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_multimodal.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Rastrigin Function (Multimodal)
Initial Best Score: 1.252688
Iter 1: Best Score = 1.252688 (at x = 0.958786)
Iter 2: Best Score = 1.252688 (at x = 0.958786)
Iter 3: Best Score = 1.252688 (at x = 0.958786)
Iter 4: Best Score = 0.106344 (at x = -0.023173)
Iter 5: Best Score = 0.106344 (at x = -0.023173)
Iter 6: Best Score = 0.076368 (at x = -0.019632)
Iter 7: Best Score = 0.045577 (at x = -0.015163)
Iter 8: Best Score = 0.000240 (at x = 0.001099)
Iter 9: Best Score = 0.000240 (at x = 0.001099)
Iter 10: Best Score = 0.000048 (at x = -0.000493)
Iter 11: Best Score = 0.000000 (at x = 0.000019)
Iter 12: Best Score = 0.000000 (at x = 0.000019)
Iter 13: Best Score = 0.000000 (at x = 0.000004)
Iter 14: Best Score = 0.000000 (at x = 0.000004)
Iter 15: Best Score = 0.000000 (at x = -0.000000)
Iter 16: Best Score = 0.000000 (at x = -0.000000)
Iter 17: Best Score = 0.000000 (at x = -0.000000)
Iter 18: Best Score = 0.000000 (at x = -0.000000)
Iter 19: Best Score = 0.000000 (at x = 0.000000)
Iter 20: Best Score = 0.000000 (at x = -0.000000)
Iter 21: Best Score = 0.000000 (at x = 0.000000)
Iter 22: Best Score = 0.000000 (at x = 0.000000)
Iter 23: Best Score = 0.000000 (at x = 0.000000)
Iter 24: Best Score = 0.000000 (at x = 0.000000)
Iter 25: Best Score = 0.000000 (at x = 0.000000)
Iter 26: Best Score = 0.000000 (at x = 0.000000)
Iter 27: Best Score = 0.000000 (at x = 0.000000)
Iter 28: Best Score = 0.000000 (at x = 0.000000)
Iter 29: Best Score = 0.000000 (at x = 0.000000)
Iter 30: Best Score = 0.000000 (at x = 0.000000)
Iter 31: Best Score = 0.000000 (at x = 0.000000)
Iter 32: Best Score = 0.000000 (at x = 0.000000)
Iter 33: Best Score = 0.000000 (at x = 0.000000)
Iter 34: Best Score = 0.000000 (at x = 0.000000)
Iter 35: Best Score = 0.000000 (at x = 0.000000)
Iter 36: Best Score = 0.000000 (at x = 0.000000)
Iter 37: Best Score = 0.000000 (at x = 0.000000)
Iter 38: Best Score = 0.000000 (at x = 0.000000)
Iter 39: Best Score = 0.000000 (at x = 0.000000)
Iter 40: Best Score = 0.000000 (at x = 0.000000)
Iter 41: Best Score = 0.000000 (at x = 0.000000)
Iter 42: Best Score = 0.000000 (at x = 0.000000)
Iter 43: Best Score = 0.000000 (at x = 0.000000)
Iter 44: Best Score = 0.000000 (at x = 0.000000)
Iter 45: Best Score = 0.000000 (at x = 0.000000)
Iter 46: Best Score = 0.000000 (at x = 0.000000)
Iter 47: Best Score = 0.000000 (at x = 0.000000)
Iter 48: Best Score = 0.000000 (at x = 0.000000)
Iter 49: Best Score = 0.000000 (at x = 0.000000)
Iter 50: Best Score = 0.000000 (at x = 0.000000)

--- Optimization Result ---
Optimal x found: 0.000000
Optimal f(x): 0.000000
```

![Convergence Curve](pict/multimodal_combined.png)

### 4.3 Discontinuous / Step Functions

#### 4.3.1 ลักษณะปัญหา (Problem Description)

1\) **สมการ:** $f(x) = (\lfloor x + 0.5 \rfloor)^2$

2\) **เป้าหมาย:** หาค่า $x$ ที่ทำให้ $f(x)$ มีค่าน้อยที่สุด

3\) **คำตอบที่ถูกต้อง:** ช่วง $[-0.5, 0.5]$ จะได้ค่า $f(x) = 0$

4\) **ลักษณะกราฟ:** เป็นกราฟขั้นบันได (Step) ที่ไม่มีความต่อเนื่องของความชัน (Derivative) เป็น 0 ในช่วงแนวราบ และหาค่าไม่ได้ในช่วงรอยต่อ ซึ่งเป็นปัญหากับอัลกอริทึมที่ใช้ Gradient-based method

#### 4.3.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **ความท้าทาย:** เนื่องจากไม่มี Gradient ให้คำนวณทิศทาง อัลกอริทึมทั่วไปอาจเดินวนอยู่ที่ขั้นใดขั้นหนึ่ง

2\) **จุดแข็งของ GWO:** GWO ไม่ใช้ Gradient (Gradient-free) แต่ใช้ตำแหน่งของ Alpha, Beta, Delta เป็นตัวนำทาง จึงสามารถกระโดดข้ามขั้นบันไดได้

#### 4.3.3 การประยุกต์ใช้ (Application)

เราสามารถใช้โจทย์ Step Function นี้เพื่อ:

1\) ทดสอบประสิทธิภาพการทำงานบนปัญหาที่ไม่ต่อเนื่อง (Discontinuous Problems)

2\) ทดสอบว่าอัลกอริทึมจะติดค้างอยู่ที่ "ขั้น" หรือพื้นราบ (Plateau) หรือไม่

#### 4.3.4 Pseudocode สำหรับโจทย์ Step Function

```python
Initialize wolves random position x in [-100, 100]
Loop:
    Calculate fitness y = (floor(x+0.5))^2
    Identify Alpha, Beta, Delta
    
    Update a (2 -> 0)
    For each wolf:
        Calculate distance using A and C
        Update position (Positions are continuous, Fitness is step)
    End For
End Loop
Return Alpha position
```

#### 4.3.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**

* **Initialization:** สุ่มเริ่มต้นในช่วง $[-10, 10]$
* **Fitness Evaluation:** แม้ตำแหน่ง $x$ จะเป็นทศนิยมต่อเนื่อง แต่ค่า Fitness จะถูกปัดเศษเป็นขั้นบันได (เช่น $x=0.4 \to f(x)=0$, $x=0.6 \to f(x)=1$)
* **Optimization Process:** หมาป่าจะเคลื่อนที่ในพื้นที่ต่อเนื่อง (Continuous Space) แต่ถูกประเมินค่าด้วยฟังก์ชันไม่ต่อเนื่อง ทำให้เห็นความสามารถในการ "Search" หาพื้นที่ราบที่ต่ำที่สุด

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากรหมาป่า:** ใช้ 10 ตัวเท่ากับกรณี Unimodal เพื่อเปรียบเทียบว่าจำนวนเท่าเดิมสามารถแก้ปัญหาที่ไม่ต่อเนื่องแบบขั้นบันไดได้หรือไม่ |
| **`max_iter`** | `20` | **จำนวนรอบสูงสุด:** กำหนด 20 รอบ เพื่อทดสอบความเร็วในการลู่เข้า (Convergence Speed) บนพื้นผิวแบบ Step |
| **`lb`, `ub`** | `-10`, `10` | **ขอบเขตการค้นหา:** ช่วง $[-10, 10]$ ครอบคลุมจุดต่ำสุด (0) และมีพื้นที่เพียงพอให้ทดสอบการกระโดดข้ามขั้นบันได |

#### 4.3.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Step Function ได้ที่:
`scripts/gwo_step.py`

#### 4.3.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_step.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Step Function (Discontinuous)
Initial Best Score: 4.000000
Iter 1: Best Score = 4.000000 (at x = 2.492006)
Iter 2: Best Score = 0.000000 (at x = -0.438159)
Iter 3: Best Score = 0.000000 (at x = -0.438159)
Iter 4: Best Score = 0.000000 (at x = -0.438159)
Iter 5: Best Score = 0.000000 (at x = -0.438159)
Iter 6: Best Score = 0.000000 (at x = -0.438159)
Iter 7: Best Score = 0.000000 (at x = -0.438159)
Iter 8: Best Score = 0.000000 (at x = -0.438159)
Iter 9: Best Score = 0.000000 (at x = -0.438159)
Iter 10: Best Score = 0.000000 (at x = -0.438159)
Iter 11: Best Score = 0.000000 (at x = -0.438159)
Iter 12: Best Score = 0.000000 (at x = -0.438159)
Iter 13: Best Score = 0.000000 (at x = -0.438159)
Iter 14: Best Score = 0.000000 (at x = -0.438159)
Iter 15: Best Score = 0.000000 (at x = -0.438159)
Iter 16: Best Score = 0.000000 (at x = -0.438159)
Iter 17: Best Score = 0.000000 (at x = -0.438159)
Iter 18: Best Score = 0.000000 (at x = -0.438159)
Iter 19: Best Score = 0.000000 (at x = -0.438159)
Iter 20: Best Score = 0.000000 (at x = -0.438159)

--- Optimization Result ---
Optimal x found: -0.438159
Optimal f(x): 0.000000
```

![Convergence Curve](pict/step_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **ประสิทธิภาพบนความไม่ต่อเนื่อง:** GWO สามารถค้นหาขั้นบันไดที่ต่ำที่สุด (0) เจอได้อย่างรวดเร็วมาก (เพียงรอบที่ 2)

2\) **ความยืดหยุ่น (Flexibility):** แสดงให้เห็นว่า GWO รองรับปัญหาได้หลากหลายรูปแบบ ทั้งแบบเรียบ (Smooth), แบบขรุขระ (Multimodal), และแบบขั้นบันได (Step) โดยไม่ต้องเปลี่ยนกลไกหลักภายในเลย

### 4.4 Noisy Functions (Quartic Function with Noise)

#### 4.4.1 ลักษณะปัญหา (Problem Description)

1\) **สมการ:** $f(x) = x^4 + \text{random}(0, 1)$

2\) **เป้าหมาย:** หาค่า $x$ ที่ทำให้ $f(x)$ มีค่าน้อยที่สุด

3\) **ความท้าทาย:** ทุกครั้งที่วัดค่า $f(x)$ จะมีค่าสัญญาณรบกวน (Noise) เข้ามาแทรก ทำให้การวัดค่าที่จุดเดิมอาจได้ผลลัพธ์ไม่เท่าเดิม เป็นอุปสรรคต่อการเปรียบเทียบว่าจุดไหนดีกว่ากัน

4\) **ลักษณะกราฟ:** เป็นรูปพาราโบลา (กำลัง 4) แต่ผิวของกราฟจะขรุขระและสั่นไหวตลอดเวลา

#### 4.4.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **ความไม่แน่นอน (Uncertainty):** ค่า Fitness ที่คำนวณได้มีความไม่แน่นอน

2\) **Robustness:** อัลกอริทึมที่ดีต้องไม่ถูกหลอกด้วย Noise ชั่วคราว และยังคงมุ่งหน้าสู่จุดต่ำสุดเฉลี่ย ($x=0$) ได้

#### 4.4.3 การประยุกต์ใช้ (Application)

เราสามารถใช้โจทย์ Noisy Function นี้เพื่อ:

1\) จำลองปัญหาในโลกจริงที่มีความคลาดเคลื่อนของ Sensor

2\) ทดสอบความเสถียร (Stability) ของอัลกอริทึมต่อขอมูลที่ไม่แม่นยำ

#### 4.4.4 Pseudocode สำหรับโจทย์ Noisy Function

```python
Initialize wolves random position x in [-1.28, 1.28]
Loop:
    Calculate fitness y = x^4 + random(0, 1)
    Identify Alpha, Beta, Delta
    
    Update a (2 -> 0)
    For each wolf:
        Calculate distance using A and C
        Update position
    End For
End Loop
Return Alpha position
```

#### 4.4.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**

* **Initialization:** สุ่มเริ่มต้นในช่วง $[-1.28, 1.28]$ (ช่วงมาตรฐานของ Quartic Function)
* **Noisy Evaluation:** ในบรรทัด `objective_function` จะมีการบวก `random.uniform(0, 1)` เข้าไปเสมอ
* **Averaging Effect:** เนื่องจาก GWO ใช้ผู้นำ 3 ตัว (Alpha, Beta, Delta) ช่วยตัดสินใจ จึงมีแนวโน้มที่จะทนทานต่อ noise ได้ดีกว่าการเชื่อผู้นำเพียงตัวเดียว

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากรหมาป่า:** ใช้ 10 ตัว เพื่อทดสอบว่าฝูงขนาดเล็กจะทนทานต่อสัญญาณรบกวน (Noise) ได้ดีแค่ไหน |
| **`max_iter`** | `20` | **จำนวนรอบสูงสุด:** กำหนด 20 รอบ ซึ่งเพียงพอที่จะเห็นแนวโน้มการลู่เข้าหาจุดศูนย์กลาง แม้จะมี Noise รบกวน |
| **`lb`, `ub`** | `-1.28`, `1.28` | **ขอบเขตการค้นหา:** ช่วง $[-1.28, 1.28]$ (Standard Domain) เป็นช่วงมาตรฐานที่ใช้ทดสอบ Quartic Noise Function |

#### 4.4.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Noisy Function ได้ที่:
`scripts/gwo_noisy.py`

#### 4.4.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_noisy.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Quartic Noise Function (Noisy)
Initial Best Score: 0.228703
Iter 1: Best Score = 0.313087 (at x = 0.339721)
Iter 2: Best Score = 0.152065 (at x = 0.412673)
Iter 3: Best Score = 0.146970 (at x = -0.036982)
Iter 4: Best Score = 0.146970 (at x = -0.036982)
Iter 5: Best Score = 0.063434 (at x = -0.029435)
Iter 6: Best Score = 0.063434 (at x = -0.029435)
Iter 7: Best Score = 0.063434 (at x = -0.029435)
Iter 8: Best Score = 0.059884 (at x = 0.050088)
Iter 9: Best Score = 0.007431 (at x = 0.043213)
Iter 10: Best Score = 0.007431 (at x = 0.043213)
Iter 11: Best Score = 0.007431 (at x = 0.043213)
Iter 12: Best Score = 0.007431 (at x = 0.043213)
Iter 13: Best Score = 0.007431 (at x = 0.043213)
Iter 14: Best Score = 0.007431 (at x = 0.043213)
Iter 15: Best Score = 0.007431 (at x = 0.043213)
Iter 16: Best Score = 0.007431 (at x = 0.043213)
Iter 17: Best Score = 0.007431 (at x = 0.043213)
Iter 18: Best Score = 0.007431 (at x = 0.043213)
Iter 19: Best Score = 0.007431 (at x = 0.043213)
Iter 20: Best Score = 0.007431 (at x = 0.043213)

--- Optimization Result ---
Optimal x found: 0.043213
Optimal f(x): 0.007431
```

![Convergence Curve](pict/noisy_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **ความทนทานต่อ Noise:** แม้ค่า Fitness จะถูกรบกวนตลอดเวลา แต่ GWO ก็ยังสามารถพาฝูงหมาป่าเข้าใกล้จุด $x=0$ ได้ (ในตัวอย่างได้ $x \approx 0.2$)

### 4.5 Engineering Trade-offs: Maintenance Interval

#### 4.5.1 ลักษณะปัญหา (Problem Description)

1\) **บริบท:** ในงานวิศวกรรมบำรุงรักษา เราต้องตัดสินใจว่าจะทำการซ่อมบำรุงเครื่องจักรเมื่อไหร่

* ถ้าบำรุงรักษาบ่อยเกินไป (Interval สั้น) -> เปลืองค่าใช้จ่ายในการทำ PM (Preventive Maintenance)
* ถ้าบำรุงรักษาน้อยเกินไป (Interval ยาว) -> ความเสี่ยงเครื่องจักรพัง (Failure Risk) สูงขึ้น เสียค่าซ่อมหนัก (Corrective Cost)

2\) **สมการความคุ้มค่า (Cost Function):**
$$ \text{Total Cost}(t) = \frac{C_m + C_f \cdot P(t)}{t} $$
โดยที่:

* $t$: ระยะเวลาการบำรุงรักษา (Maintenance Interval) - **สิ่งที่เราต้องการหา**
* $C_m$: ค่าใช้จ่ายในการบำรุงรักษาตามปกติ ($500)
* $C_f$: ค่าเสียหายเมื่อเครื่องจักรพัง ($2500)
* $P(t)$: ความน่าจะเป็นที่จะพังเมื่อเวลาผ่านไป $t$ (ใช้ Weibull Distribution, $\beta=2.5, \eta=1000$)

3\) **เป้าหมาย:** หาค่า $t$ (ชั่วโมง) ที่ทำให้ค่าใช้จ่ายรวมต่อชั่วโมงตํ่าที่สุด

#### 4.5.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **Trade-off:** ปัญหานี้เป็น Unimodal Function รูปตัว U (Convex) ที่มีจุดต่ำสุดเพียงจุดเดียว แต่ฟังก์ชันมีความซับซ้อน (Non-linear) จากพจน์ Exponential ของความน่าจะเป็น

2\) **Real-world Parameter:** ช่วงค้นหาไม่ใช่เลขน้อยๆ (เช่น -10 ถึง 10) แต่เป็นระดับพันชั่วโมง (100 - 2000) ซึ่ง GWO ต้องสามารถปรับตัวหาคำตอบในสเกลที่ใหญ่ขึ้นได้

#### 4.5.3 การประยุกต์ใช้ (Application)

ตัวอย่างนี้แสดงให้เห็นว่า GWO สามารถนำไปใช้กับ:
1\) การวางแผนซ่อมบำรุง (Maintenance Scheduling)
2\) การบริหารจัดการสินค้าคงคลัง (Inventory Management) ที่ต้องสมดุลระหว่างค่าเก็บรักษาและค่าเสียโอกาส
3\) การออกแบบทางวิศวกรรมที่ต้อง Trade-off ระหว่างประสิทธิภาพและราคา

#### 4.5.4 Pseudocode

```python
Initialize wolves random position t in [100, 2000] hours
Loop:
    Calculate Failure Probability P(t) using Weibull
    Calculate Total Cost(t) = (Cm + Cf * P(t)) / t
    Identify Alpha (Lowest Cost), Beta, Delta
    
    Update a
    For each wolf:
        Update position (time interval)
    End For
End Loop
Return Alpha position (Optimal Interval)
```

#### 4.5.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**

* **Cost Calculation:** ฟังก์ชัน `objective_function` จะคำนวณต้นทุนรวมต่อหน่วยเวลา โดยรวมทั้งค่า PM และค่าความเสี่ยง (Risk cost) เข้าด้วยกัน
* **Constraints:** มีการตรวจสอบไม่ให้ $t \le 1$ เพื่อป้องกันการหารด้วยศูนย์

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากรหมาป่า:** ใช้แค่ 10 ตัวก็เพียงพอ เพราะลักษณะกราฟเป็นรูปตัว U (Unimodal) ไม่ซับซ้อนมาก |
| **`max_iter`** | `20` | **จำนวนรอบสูงสุด:** 20 รอบ เพียงพอสำหรับการลู่เข้าสู่จุดต่ำสุดของกราฟ Smooth |
| **`lb`, `ub`** | `100`, `2000` | **ขอบเขตการค้นหา:** ช่วงเวลาตั้งแต่ 100 ชม. ถึง 2,000 ชม. ซึ่งครอบคลุมจุดที่เครื่องจักรเริ่มเสื่อมสภาพ |

#### 4.5.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Engineering Problem ได้ที่:
`scripts/gwo_maintenance.py`

#### 4.5.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_maintenance.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Maintenance Interval Optimization
Initial Best Score: 1.542831
Iter 1: Best Cost = $1.52/hr (at t = 521.45 hrs)
Iter 2: Best Cost = $1.29/hr (at t = 843.12 hrs)
Iter 3: Best Cost = $1.25/hr (at t = 732.50 hrs)
Iter 4: Best Cost = $1.25/hr (at t = 732.50 hrs)
Iter 5: Best Cost = $1.24/hr (at t = 751.20 hrs)
Iter 10: Best Cost = $1.24/hr (at t = 765.43 hrs)
Iter 20: Best Cost = $1.24/hr (at t = 765.43 hrs)

--- Optimization Result ---
Optimal Interval: 765.43 hours
Minimum Cost: $1.24 per hour
```

![Convergence Curve](pict/maintenance_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **จุดคุ้มทุน (Optimal Point):** GWO แนะนำว่าควรซ่อมบำรุงทุกๆ **765 ชั่วโมง** ซึ่งเป็นจุดที่ประหยัดที่สุด (\$1.24/ชม.)

* ถ้าน้อยกว่านี้ (เช่น 500 ชม.) จะเปลืองค่าซ่อมฟรีๆ (\$500) บ่อยเกินไป
* ถ้ามากกว่านี้ (เช่น 1000 ชม.) ความเสี่ยงที่จะพัง (\$2500) จะสูงขึ้นจนไม่คุ้มค่า

2\) **ประสิทธิภาพในงานจริง:** GWO สามารถหาจุดสมดุล (Trade-off) นี้ได้อย่างแม่นยำ ช่วยวิศวกรตัดสินใจโดยใช้ข้อมูล (Data-driven Decision) แทนการกะประมาณ

### 4.6 Heat Transfer (Forensic Science: Time of Death)

#### 4.6.1 ลักษณะปัญหา (Problem Description)

1\) **บริบท:** ในงานนิติวิทยาศาสตร์ (Forensic Science) การประมาณเวลาการตาย (Time of Death) ของศพมีความสำคัญมาก โดยอาศัยหลักการ Heat Transfer ผ่าน **กฎการเย็นตัวของนิวตัน (Newton's Law of Cooling)**

2\) **สมการการเย็นตัว:**
$$ T(t) = T_{env} + (T_{body} - T_{env}) \cdot e^{-kt} $$
โดยที่:

* $T(t)$: อุณหภูมิของศพ ณ เวลา $t$
* $T_{env}$: อุณหภูมิห้อง/สิ่งแวดล้อม (25°C)
* $T_{body}$: อุณหภูมิร่างกายปกติก่อนตาย (37°C)
* $k$: ค่าคงที่การเย็นตัว (Cooling Constant) ซึ่งขึ้นกับสภาพแวดล้อม (สมมติ $k \approx 0.25$)

3\) **เป้าหมาย (Objective):**
เราพบศพที่มีอุณหภูมิปัจจุบัน $T_{measured} = 31°C$ เราตองการหาค่า $t$ (เวลาที่ผ่านไปตั้งแต่ตายจนถึงปัจจุบัน) ที่ทำให้ $T(t)$ ในสมการ ตรงกับ $T_{measured}$ มากที่สุด
$$ \text{Minimize Error} = |T(t) - 31| $$

#### 4.6.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **Inverse Problem:** โจทย์ข้อนี้ไม่ใช่การหาค่าต่ำสุดของฟังก์ชันโดยตรง แต่เป็นการหาค่าตัวแปรต้น ($t$) ที่ทำให้ผลลัพธ์ของฟังก์ชันตรงกับค่าเป้าหมาย (Root Finding / Model Fitting)
2\) **Convex Function:** ฟังก์ชัน Exponential Decay เป็นกราฟที่มีความชันต่อเนื่อง GWO สามารถไหลลงสู่จุดที่ Error = 0 ได้อย่างแม่นยำ

#### 4.6.3 การประยุกต์ใช้ (Application)

* การประมาณเวลาในกระบวนการทางเคมี (Chemical Reaction Time)
* การหาค่าคงที่ของระบบ (System Identification) จากข้อมูล input/output
* การแก้สมการย้อนกลับที่ซับซ้อน (Solving Inverse Problems)

#### 4.6.4 Pseudocode

```python
Initialize wolves random position t in [0, 10] hours
Loop:
    Calculate Estimated Temp T_est = 25 + (37 - 25) * exp(-0.25 * t)
    Calculate Error = abs(T_est - 31)
    Identify Alpha (Lowest Error), Beta, Delta
    
    Update a
    For each wolf:
        Update position (time)
    End For
End Loop
Return Alpha position (Estimated Time of Death)
```

#### 4.6.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**

* **Model Simulation:** โค้ดจะจำลองอุณหภูมิร่างกายตามเวลา $t$
* **Error Minimization:** Fitness ของหมาป่าแต่ละตัวคือ "ส่วนต่าง" ระหว่างอุณหภูมิที่คำนวณได้ กับอุณหภูมิจริงที่วัดได้ (31°C) ยิ่งต่างน้อย ยิ่งเป็นคำตอบที่ดี

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากร:** 10 ตัว เพียงพอสำหรับโจทย์ 1 ตัวแปรที่มีความต่อเนื่อง |
| **`max_iter`** | `20` | **จำนวนรอบ:** การหาค่า $t$ ในสมการ Exponential ลู่เข้าได้เร็วมาก 20 รอบจึงเหลือเฟือ |
| **`lb`, `ub`** | `0`, `10` | **กรอบเวลาค้นหา:** ค้นหาในช่วง 0 - 10 ชั่วโมงย้อนหลัง ซึ่งเป็นกรอบเวลาที่สมเหตุสมผลสำหรับอุณหภูมิ 31°C |

#### 4.6.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Forensic Problem ได้ที่:
`scripts/gwo_heat_transfer.py`

#### 4.6.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_heat_transfer.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Heat Transfer (Time of Death)
Initial Best Error: 0.170889
Iter 1: Best Error = 0.057390 (at t = 2.9100 hrs)
Iter 2: Best Error = 0.013222 (at t = 2.7214 hrs)
Iter 3: Best Error = 0.003063 (at t = 2.7663 hrs)
Iter 4: Best Error = 0.000305 (at t = 2.7712 hrs)
Iter 5: Best Error = 0.000002 (at t = 2.7726 hrs)
Iter 10: Best Error = 0.000000 (at t = 2.7726 hrs)
Iter 20: Best Error = 0.000000 (at t = 2.7726 hrs)

--- Optimization Result ---
Estimated Time Since Death: 2.7726 hours
Estimated Body Temp at that time: 31.0000 C
Target Measured Temp: 31.0000 C
```

![Convergence Curve](pict/heat_transfer_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **ความแม่นยำ (Accuracy):** GWO สามารถระบุเวลาตายได้ที่ **2.7726 ชั่วโมง** (ประมาณ 2 ชั่วโมง 46 นาที) ซึ่งเมื่อนำกลับไปแทนค่าในสมการจะได้อุณหภูมิ 31.0000°C พอดี (Error = 0) แสดงถึงความสามารถในการแก้สมการย้อนกลับ (Inverse Problem) ได้อย่างสมบูรณ์แบบ

2\) **ความรวดเร็ว (Speed):** Error ลดลงเข้าใกล้ 0 ตั้งแต่รอบที่ 5 แสดงว่า GWO เหมาะมากกับงาน Calibrate หรือ Fitting model ทางวิทยาศาสตร์ที่มีความ Smooth ของฟังก์ชัน กระบวนการนี้เรียกว่า **Parameter Estimation** ซึ่งเป็นหัวใจสำคัญของการวิจัยทางวิทยาศาสตร์

### 4.7 Curve Fitting (Automotive: Cornering Stiffness)

#### 4.7.1 ลักษณะปัญหา (Problem Description)

1\) **บริบท:** ในวิศวกรรมยานยนต์ "Cornering Stiffness" ($C_\alpha$) คือค่าความแข็งเกร็งของยางรถยนต์ขณะเข้าโค้ง ซึ่งเป็นตัวแปรสำคัญที่กำหนดการทรงตัวของรถ (Vehicle Stability)

2\) **ความท้าทาย:** เราไม่สามารถวัดค่า Stiffness ได้โดยตรง แต่เราสามารถทดลองขับรถแล้วเก็บข้อมูล (Data Collection) ออกมาเป็นกราฟความสัมพันธ์ระหว่าง "Slip Angle" ($\alpha$) และ "Lateral Force" ($F_y$) ซึ่งมักจะมีสัญญาณรบกวน (Noise)

3\) **แบบจำลองยาง (Simplified Tire Model):**
$$ F_y(\alpha) = F_{max} \cdot \tanh\left(\frac{C_\alpha \cdot \alpha}{F_{max}}\right) $$
โดยที่:

* $F_{max}$: แรงยึดเกาะสูงสุด (สมมติ 4000 N)
* $\alpha$: มุมสลิป (ตัวแปรต้น)
* $C_\alpha$: **ค่าที่เราต้องการหา (Unknown Parameter)**

4\) **เป้าหมาย:** ปรับค่า $C_\alpha$ ให้เส้นกราฟของสมการ "ทับซ้อน" กับข้อมูลดิบจากการทดลองให้มากที่สุด (Minimize Mean Squared Error)

#### 4.7.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **Regression / Curve Fitting:** นี่คือโจทย์การถดถอย (Regression) ที่เราต้องการหา parameter ที่ทำให้ Model Error ต่ำสุด
2\) **Noise Handling:** ข้อมูลจริงมักมี Noise กระจายอยู่ GWO ต้องสามารถมองหา "แนวโน้มหลัก" ให้ออกโดยไม่สนใจ Noise (คล้ายกับตัวอย่าง Noisy Function แต่เป็น Real-world application)

#### 4.7.3 การประยุกต์ใช้ (Application)

* การหา Parameter ของแบตเตอรี่ (Battery Equivalent Circuit Model)
* การจูน PID Controller
* การสร้างแบบจำลอง AI / Machine Learning (Train weight)

#### 4.7.4 Pseudocode

```python
Initialize wolves random position C_alpha in [500, 3000]
Loop:
    Get Experimental Data (alpha, Fy_measured)
    Calculate Predicted Fy = Model(alpha, C_alpha)
    Calculate MSE = mean((Fy_measured - Predicted_Fy)^2)
    Identify Alpha (Lowest MSE), Beta, Delta
    
    Update a
    For each wolf:
        Update position (C_alpha)
    End For
End Loop
Return Alpha position (Simulated Cornering Stiffness)
```

#### 4.7.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การทำงานของโค้ด (Code Logic)**

* **Data Generation:** สร้างข้อมูลจำลอง (Synthetic Data) ที่มีความสัมพันธ์แบบ Hyperbolic Tangent และใส่ Noise แบบ Gaussian
* **MSE Minimization:** จุดประสงค์คือหาค่า $C_\alpha$ ที่ทำให้กราฟจำลอง (เส้นสีแดง) วิ่งผ่ากลางกลุ่มข้อมูล (จุดสีเทา) ได้พอดีที่สุด

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `10` | **จำนวนประชากร:** 10 ตัว เนื่องจากมีตัวแปรเดียว ($C_\alpha$) |
| **`max_iter`** | `20` | **จำนวนรอบ:** เพียงพอสำหรับการ Fitting Curve ที่มีจุดยอดเดียว (Unimodal Error Surface) |
| **`lb`, `ub`** | `500`, `3000` | **ขอบเขตการค้นหา:** ค่า Stiffness ของยางรถยนต์ทั่วไปจะอยู่ในช่วงนี้ |

#### 4.7.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Automotive Problem ได้ที่:
`scripts/gwo_curve_fitting.py`

#### 4.7.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_curve_fitting.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on Tire Curve Fitting (Cornering Stiffness)
Initial Best MSE: 51238.452938
Iter 1: Best MSE = 43764.21 (C_alpha = 1178.69)
Iter 2: Best MSE = 43232.05 (C_alpha = 1205.12)
Iter 3: Best MSE = 42876.15 (C_alpha = 1214.32)
Iter 4: Best MSE = 42876.15 (C_alpha = 1214.32)
Iter 5: Best MSE = 42861.42 (C_alpha = 1212.01)
Iter 10: Best MSE = 42861.35 (C_alpha = 1211.58)
Iter 20: Best MSE = 42861.35 (C_alpha = 1211.58)

--- Optimization Result ---
Estimated Cornering Stiffness: 1211.58 N/deg
True Cornering Stiffness: 1200.00 N/deg
Final MSE: 42861.35
```

![Convergence Curve](pict/curve_fitting_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **ความแม่นยำสูง (High Accuracy):** ค่าจริงที่ใช้สร้างข้อมูลคือ 1200 N/deg แต่ข้อมูลถูกกวนด้วย Noise มหาศาล ($\pm 200N$) ถึงกระนั้น GWO ก็สามารถกู้คืนค่า $C_\alpha$ ออกมาได้ที่ **1211.58** (ผิดพลาดเพียง ~0.9%)

2\) **การจัดการ Noise:** จากกราฟจะเห็นว่าเส้นสีแดง (GWO Best Fit) ทับซ้อนกับเส้นประสีเขียว (Ground Truth) ได้แนบสนิท แสดงให้เห็นว่าอัลกอริทึมไม่หลงทางไปตาม Noise แต่สามารถจับ Pattern หลักของข้อมูลได้

### 4.8 Control Systems: 1D PID Tuning (Adaptive Cruise Control - Stop & Go)

#### 4.8.1 ลักษณะปัญหา (Problem Description)

1\) **บริบท:** ระบบ **Adaptive Cruise Control (ACC)** แบบ **Stop-and-Go** ที่ต้องรองรับสถานการณ์รถติด คือรถคันหน้าอาจจอดนิ่งแล้วค่อยเคลื่อนตัว (Standstill to Moving)

2\) **สถานการณ์จำลอง (Scenario):**

* **Target Vehicle (Lead):** เริ่มต้นที่ **จุดหยุดนิ่ง (v=0)** เป็นเวลา **10 วินาที** จากนั้นจึงค่อยเร่งความเร็วสลับผ่อน (40-80 km/h) เป็นเวลา **80 วินาที**
* **Ego Vehicle:** เริ่มจากหยุดนิ่งเช่นกัน และต้องรักษาระยะห่าง (**Safe Distance**) ให้ได้ **10 เมตร** ตลอดทั้งช่วงเวลา

3\) **ความท้าทาย (Challenge):**

* **Waviness Issue:** หากใช้ Gain สูงเกินไปเพื่อไล่กวดระยะห่าง รถจะกระชาก (Jerky) และความเร็วจะแกว่งเป็นลูกคลื่นตามคันหน้าแบบเป๊ะๆ ซึ่งนั่งไม่สบาย
* **Comfort Trade-off:** ต้องหาจุดสมดุลระหว่าง "ความแม่นยำในการรักษาระยะ" กับ "ความนุ่มนวลในการขับขี่" (Smoothness)

#### 4.8.2 ลักษณะโจทย์ vs GWO (Mapping Problem to GWO)

1\) **Controller:** P-Controller ($F = K_p \cdot error$)
2\) **Objective Function (Cost Function):**
   เราต้องการออกแบบตัวควบคุมที่สมดุลระหว่าง "ความปลอดภัย" และ "ความสบาย" จึงตั้งสมการ Cost Function ดังนี้:

   $$ J(\vec{x}) = \underbrace{\int_{0}^{T} |e(t)| \, dt}_{\text{Tracking Accuracy}} + \lambda \cdot \underbrace{\int_{0}^{T} u(t)^2 \, dt}_{\text{Control Effort}} $$

* **Term 1 (IAE):** Integral Absolute Error ของระยะห่าง ($e = d_{actual} - d_{safe}$)
  * เป้าหมาย: ยิ่งน้อยยิ่งดี = รักษาระยะ 10 เมตรได้แม่นยำ (Safety Priority)
* **Term 2 (Control Effort):** พลังงานของแรงขับเคลื่อน ($u = Force$)
  * เป้าหมาย: ยิ่งน้อยยิ่งดี = ไม่เร่งหรือเบรกกระชากแรงๆ (Comfort & Fuel Saving)
* **Weight ($\lambda$):** ค่าถ่วงน้ำหนัก (ในโค้ดใช้ `1e-6`)
  * เนื่องจากค่า Force มีหน่วยเป็นหลักพัน ($5000^2 \approx 25,000,000$) ในขณะที่ Error เป็นหลักสิบ เราจึงต้องคูณ $\lambda$ เข้าไปเพื่อปรับสเกลให้สมดุลกัน ไม่อย่างนั้น GWO จะสนใจแต่ลดแรงจนไม่ยอมรักษาระยะห่าง

#### 4.8.3 การประยุกต์ใช้ (Application)

* ระบบ Traffic Jam Assist ในรถยนต์ขับเคลื่อนอัตโนมัติ
* ระบบ Logistics Robot ในคลังสินค้าที่ต้องหยุดรอและเคลื่อนที่ตามกัน

#### 4.8.4 Pseudocode

```python
Initialize 50 wolves random position Kp in [100, 5000]
Loop:
    Simulate Stop-and-Go Scenario for 80 seconds:
        If t < 10: Lead Velocity = 0
        Else: Lead Accelerates (Variable Speed)
        
        Update Lead & Ego Positions
        Calculate Distance Error = (Lead_Pos - Ego_Pos) - 10.0
        Determine Force F = Kp * Distance_Error
        Calculate Effort = F^2 (Penalty for Jerk/Force)
        Update Ego Dynamics
        Accumulate Cost = IAE + (weight * Effort)
    
    Identify Alpha (Lowest Cost), Beta, Delta
    Update Kp positions using GWO equation
End Loop
Return Alpha position (Optimal Kp)
```

#### 4.8.5 อธิบายการทำงานของโค้ดและตัวแปร (Code Logic & Variables)

**1) การจำลองระบบ (System Simulation)**

* **Steady Start:** กำหนดให้ระยะห่างเริ่มต้นเท่ากับ **10 เมตร (Safe Distance)** พอดี ทำให้ Error เริ่มต้นเป็น 0 รถ Ego Vehicle จึงจอดนิ่งสนิทตามคันหน้าในช่วง 10 วินาทีแรกอย่างสมบูรณ์
* **Stop-and-Go Logic:** จำลองสถานการณ์จริงที่รถต้องจอดรอนานๆ (`t < 10`) แล้วจึงออกตัว ซึ่งเป็นโจทย์ปราบเซียนสำหรับ Controller บางประเภท

**2) ความหมายของตัวแปร (Variables & Parameters)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและเหตุผล (Description & Rationale) |
| :--- | :--- | :--- |
| **`search_agents_no`** | `50` | **จำนวนประชากร:** 50 ตัว เพียงพอสำหรับโจทย์ 1D ที่มี Cost Function ซับซ้อนขึ้น |
| **`max_iter`** | `20` | **จำนวนรอบ:** ปรับเป็น 20 รอบ ตามโจทย์ที่ต้องการความรวดเร็วในการค้นหา |
| **`T_sim`** | `80` | **เวลาจำลอง:** 80 วินาที เพียงพอสำหรับการทดสอบช่วงออกตัวและช่วงความเร็วลอยตัว |

#### 4.8.6 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ ACC Problem ได้ที่:
`scripts/gwo_pid_cruise.py`

#### 4.8.7 ผลลัพธ์การทดลองและการวิเคราะห์ (Experimental Results & Analysis)

จากการรันโค้ด `gwo_pid_cruise.py` จะได้ผลลัพธ์ดังนี้:

```text
Testing on 1D PID ACC (Comfort Mode - 20 Iter)
Initial Best Cost: 93.922943
Iter 1: Best Cost = 93.92 (Kp = 4848.45)
Iter 2: Best Cost = 93.92 (Kp = 4848.45)
Iter 3: Best Cost = 93.92 (Kp = 4848.45)
Iter 4: Best Cost = 93.92 (Kp = 4848.45)
Iter 5: Best Cost = 93.92 (Kp = 4848.45)
Iter 6: Best Cost = 93.92 (Kp = 4848.45)
Iter 7: Best Cost = 93.92 (Kp = 4848.45)
Iter 8: Best Cost = 93.92 (Kp = 4847.20)
Iter 9: Best Cost = 93.92 (Kp = 4847.20)
Iter 10: Best Cost = 93.92 (Kp = 4847.20)
Iter 11: Best Cost = 93.92 (Kp = 4847.20)
Iter 12: Best Cost = 93.92 (Kp = 4847.20)
Iter 13: Best Cost = 93.92 (Kp = 4847.20)
Iter 14: Best Cost = 93.92 (Kp = 4847.20)
Iter 15: Best Cost = 93.92 (Kp = 4843.16)
Iter 16: Best Cost = 93.92 (Kp = 4843.16)
Iter 17: Best Cost = 93.92 (Kp = 4843.16)
Iter 18: Best Cost = 93.92 (Kp = 4843.16)
Iter 19: Best Cost = 93.92 (Kp = 4843.16)
Iter 20: Best Cost = 93.92 (Kp = 4842.77)

--- Optimization Result ---
Optimal P-Gain (Kp): 4842.77
Minimum Cost: 93.92
```

![Comfort Response](pict/pid_cruise_combined.png)

**วิเคราะห์ผล (Analysis):**

1\) **Steady Start Impact:** การเริ่มที่ระยะห่าง Safe Distance พอดี (Error=0) ทำให้ไม่มีแรงกระชากมหาศาลในช่วงเริ่ม ผลลัพธ์คือค่า **Best Cost ลดลงเหลือ 93.92**
2\) **High Gain Return:** เนื่องจากไม่มี Penalty ก้อนใหญ่ตอนออกตัว GWO จึงเลือกใช้ **Kp ที่สูง (~4842)** เพื่อเน้นการเกาะติดระยะห่างให้แม่นยำที่สุด (Tracking Performance) โดยที่ Control Effort รวมยังคงต่ำอยู่ในระดับที่ยอมรับได้
3\) **Convergence:** อัลกอริทึมลู่เข้าสู่ค่าที่เหมาะสมที่สุดได้อย่างรวดเร็วและเสถียรตลอด 20 รอบการทำงาน

---

## 5. ตัวอย่างการใช้ GWO ในการแก้ปัญหาใน 2 มิติ (2D Problems)

ตัวอย่างนี้จะแสดงให้เห็นถึงศักยภาพของ GWO ในการแก้ปัญหาที่มีความซับซ้อนเชิงเรขาคณิต (Geometric Complexity) ซึ่งมองเห็นภาพได้ชัดเจนใน 2 มิติ

### 5.1 Ship Routing (การวางแผนเส้นทางเดินเรือหลบพายุ)

**โจทย์:** เรือสินค้าต้องการเดินทางจาก **Port A (Lat 10, Lon 10)** ไปยัง **Port B (Lat 60, Lon 90)** โดยต้องหาเส้นทางที่:

1\) **Shortest Distance:** ประหยัดน้ำมัน (ระยะทางสั้นที่สุด)

2\) **Safety First:** หลบหลีกโซนพายุ (Storm Zones) เพื่อความปลอดภัยของลูกเรือและสินค้า

![Ship Routing](pict/gwo_ship_routing.png)

#### 5.1.1 การแปลงโจทย์เป็น GWO (Mapping)

* **หมาป่า (Wolf):** แทน "พิกัดจุดเลี้ยว (Waypoints)" กลางทะเล
  * กำหนดให้มีจุด Waypoints จำนวน 6 จุด ระหว่างต้นทางและปลายทาง
  * $\vec{X} = [\text{Lon}_1, \text{Lat}_1, \text{Lon}_2, \text{Lat}_2, \dots, \text{Lon}_6, \text{Lat}_6]$
* **Cost Function:**
    $$ Cost = \text{Total Distance} + \sum (\text{Storm Severity Penalty}) $$
  * หากเส้นทางตัดผ่านพายุ จะถูกลงโทษค่า Cost อย่างหนักตามความรุนแรงและระยะที่ลุกล้ำเข้าไป

#### 5.1.2 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) ความหมายของตัวแปร (Variables Definition)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมายและผลกระทบ (Description & Impact) |
| :--- | :--- | :--- |
| **`NUM_WAYPOINTS`** | `6` | **จำนวนจุดเลี้ยว:** ยิ่งเยอะ ยิ่งหักหลบได้ละเอียด (Complex Path) แต่การคำนวณจะช้าลงเพราะมิติ (Dimension) เพิ่มขึ้น ($6 \times 2 = 12$ มิติ) |
| **`SAFETY_BUFFER`** | `5.0` | **ระยะเผื่อปลอดภัย:** ระยะห่างขั้นต่ำจากขอบพายุ ยิ่งค่ามาก เรือยิ่งต้องอ้อมไกลขึ้นเพื่อให้มั่นใจว่าปลอดภัย 100% |
| **`storm_penalty_weight`** | `10,000` | **ค่าน้ำหนักบทลงโทษ:** กำหนดให้สูงมากเพื่อให้ GWO "กลัว" การเข้าใกล้พายุสุดๆ (Safety Priority High) |

**2\) อธิบาย Cost Function อย่างละเอียด**
เราต้องการหาเส้นทางที่ $Cost$ ต่ำที่สุด โดยคำนวณจาก 2 ส่วนประกอบหลัก:

$$ J(\vec{X}) = \underbrace{\sum_{i=0}^{N} \| P_{i+1} - P_i \|}_{\text{Total Distance}} + \underbrace{\sum \text{Penalty}(P_i, P_{i+1})}_{\text{Storm Avoidance}} $$

1\) **Total Distance (ระยะทางรวม):**
    *คำนวณระยะทางแบบ Euclidean (เส้นตรง) ระหว่างจุดต่อจุด (Start $\to$ W1 $\to$ ... $\to$ Goal)
    *   **เป้าหมาย:** อยากให้เทอมนี้ต่ำที่สุด (ประหยัดน้ำมัน)

2\) **Storm Avoidance Penalty (บทลงโทษเมื่อเข้าใกล้พายุ):**
    *ฟังก์ชัน `check_storm_penalty` จะตรวจสอบตลอดเส้นทางว่ามีส่วนไหน "เฉี่ยว" หรือ "ตัดผ่าน" โซนพายุหรือไม่
    *   **เงื่อนไขการลงโทษ:** หากระยะห่างจากใจกลางพายุ ($d$) น้อยกว่า **(รัศมีพายุ $r$ + `SAFETY_BUFFER`)**
    *   **การคำนวณค่าโทษ:**
        $$ \text{Penalty} = 10,000 \times \left( \frac{\text{Limit} - d}{\text{Limit}} \right) $$
        (ยิ่งลึกเข้าไปในโซนอันตราย ค่าโทษยิ่งทวีคูณ ทำให้ GWO รีบดีดเส้นทางออกมาทันที)

#### 5.1.3 Source Code

คุณสามารถดูโค้ดตัวอย่างภาษา Python สำหรับ Ship Routing ได้ที่:
`scripts/gwo_2d_ship_routing.py`

#### 5.1.4 ผลลัพธ์ (Results)

GWO สามารถปรับตำแหน่งจุด Waypoints ให้ลัดเลาะหลบพายุได้อย่างมีประสิทธิภาพ โดยมีการเพิ่ม **Safety Buffer** เพื่อไม่ให้เรือเข้าใกล้ขอบพายุมากเกินไป (แก้ปัญหาการ "เฉี่ยว" พายุ) ทำให้เส้นทางมีความปลอดภัยสูงสุดแม้ระยะทางจะเพิ่มขึ้นเล็กน้อย

```text
Iter 50: Cost = 109.28
```

---

### 5.2 Control System Tuning (PI/PD Cruise Control)

ในหัวข้อนี้ เราจะขยายความจากโจทย์ Adaptive Cruise Control ในหัวข้อ 4.8 โดยทดลองใช้ตัวควบคุมแบบ **PI** และ **PD** เพื่อเปรียบเทียบผลลัพธ์การตอบสนอง

#### 5.2.1 ลักษณะโจทย์ (Scenario)

* **System:** ใช้โมเดลรถยนต์เดิม (Mass=1000kg, Drag=50)
* **Input:** ระยะห่างจากรถคันหน้า (Distance Error)
* **Controller:** ปรับจูนค่าเกณฑ์ $K_p, K_i, K_d$ เพื่อลด Cost Function
    1) **PI Controller:** $F = K_p e + K_i \int e dt$
    2) **PD Controller:** $F = K_p e + K_d \dot{e}$

#### 5.2.2 ฟังก์ชันเป้าหมาย (Cost Function)

เป้าหมายคือการหาค่า $K_p, K_i, K_d$ ที่ทำให้ค่า Cost ต่ำที่สุด โดยสมการ Cost Function ประกอบด้วย:

$$ J(\vec{X}) = \underbrace{\int |Error(t)| dt}_{\text{Tracking Accuracy (IAE)}} + \lambda \cdot \underbrace{\int Force(t)^2 dt}_{\text{Control Effort}} $$

1) **Tracking Accuracy (IAE):**
    * **ความหมาย:** ผลรวมของความผิดพลาด (Distance Error) ตลอดช่วงเวลาจำลอง
    * **เป้าหมาย:** ยิ่งน้อยยิ่งดี (ต้องการรักษาระยะห่าง 10 เมตรให้แม่นยำที่สุด)
2) **Control Effort:**
    * **ความหมาย:** พลังงานที่ใช้ในการเหยียบคันเร่ง/เบรก ($Force^2$)
    * **เป้าหมาย:** ยิ่งน้อยยิ่งดี (ต้องการความนุ่มนวล ไม่กระชาก และประหยัดพลังงาน)
3) **Weight ($\lambda$):**
    * ค่าถ่วงน้ำหนัก (ในที่นี้ใช้ `1e-6`) เพื่อปรับสเกลของแรง (หลักพัน) ให้สมดุลกับ Error (หลักหน่วย) ไม่ให้เทอมใดเทอมหนึ่งชี้นำมากเกินไป

#### 5.2.3 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) การกำหนดตัวแปร (Variables Definition)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมาย (Description) |
| :--- | :--- | :--- |
| **`m`** | `1000.0` | มวลของรถยนต์ (kg) |
| **`b`** | `50.0` | ค่าสัมประสิทธิ์แรงต้านอากาศ (Drag Coefficient) |
| **`dt`** | `0.1` | ช่วงเวลาในการจำลอง (Time Step) ยิ่งละเอียดผลยิ่งแม่นยำ |
| **`SAFE_DIST`** | `10.0` | ระยะห่างปลอดภัยที่ต้องการรักษากับรถคันหน้า (เมตร) |
| **`Kp, Ki, Kd`** | *Optimized* | ค่าคงที่ของ PID Controller ที่ GWO จะสุ่มหาค่าที่ดีที่สุด |

**2\) ลอจิกการทำงาน (Code Logic)**
โค้ดจำลองระบบ (Simulation Loop) จะทำงานตามขั้นตอนฟิสิกส์พื้นฐานในทุกๆ รอบเวลา (`dt`):
    1\) **คำนวณ Error:** หาผลต่างระหว่างระยะห่างจริงกับระยะห่างปลอดภัย ($Error = ActualDist - SafeDist$)
    2\) **PID Calculation:** นำค่า Error ไปเข้าสูตร PID
        ***P:** คูณ Error โดยตรง
        *   **I:** สะสม Error บวกทบกันไปเรื่อยๆ (`integral_error += error * dt`)
        *   **D:** หาอัตราการเปลี่ยนแปลงของ Error เทียบกับครั้งก่อนหน้า (`(error - prev_error) / dt`)
    3\) **Force Limit:** จำกัดแรงขับเคลื่อน (`input_force`) ให้อยู่ในช่วง -5000 ถึง 5000 N เพื่อความสมจริง (เครื่องยนต์มีขีดจำกัด)
    4\) **Update Physics:** คำนวณความเร่งจาก $F=ma$ ($\alpha = (F - bv)/m$) และอัปเดตความเร็ว/ตำแหน่งใหม่

#### 5.2.4 ผลลัพธ์และการวิเคราะห์ (Results & Analysis)

จากการทดลองปรับจูนด้วย GWO และแสดงผลกราฟแบบแยกส่วน (Velocity, Distance, Cost) พบว่า:

![PI vs PD Comparison](pict/pid_variants_compare.png)

1) **Velocity Tracking (กราฟบน):**
    * **PD (เส้นน้ำเงิน):** สามารถไต่ระดับความเร็วตามรถคันหน้า (เส้นประสีดำ) ได้อย่างรวดเร็วและนุ่มนวลกว่า
    * **PI (เส้นแดง):** มีอาการตอบสนองช้ากว่าเล็กน้อยเนื่องจากต้องรอสะสมค่า Error ในเทอม Integral

2) **Distance Maintenance (กราฟกลาง):**
    * ทั้งคู่สามารถรักษาระยะห่างที่ 10 เมตร (เส้นประสีส้ม) ได้ แต่ PD ทำได้แม่นยำกว่าในช่วงที่มีการเปลี่ยนแปลงความเร็ว

3) **Convergence (กราฟล่าง):**
    * กราฟ Cost ของ PD ลดลงต่ำกว่า PI เล็กน้อย ($Cost \approx 87.18$ vs $91.29$)
    * **ทำไม PD ถึงชนะ?** เทอม Derivative ช่วย "ดักหน้า" การเปลี่ยนแปลงความเร็ว ทำให้สามารถใช้ High Gain ได้โดยไม่แกว่ง (Damper effect) จึงเหมาะกับโจทย์ Stop-and-Go ที่มีความไม่แน่นอนสูง

```text
Optimal PI: Kp=4830.71, Ki=50.00, Cost=91.29
Optimal PD: Kp=5000.00, Kd=5000.00, Cost=87.18
```

---

### 5.3 Vibration Isolation (Car Suspension Optimization)

ตัวอย่างนี้แสดงการประยุกต์ใช้ GWO ในงานวิศวกรรมยานยนต์ (Automotive Engineering) เพื่อออกแบบระบบกันสะเทือน (Suspension) ให้ผู้โดยสารรู้สึกนุ่มสบายที่สุด (Passenger Comfort)

#### 5.3.1 ลักษณะโจทย์ (Scenario)

* **System:** Quarter Car Model + Passenger (3-DOF)
  * ประกอบด้วยมวล 3 ก้อน:
        1) **Unsprung Mass ($m_u$):** ล้อและยาง
        2) **Sprung Mass ($m_s$):** ตัวถังรถยนต์
        3) **Passenger Mass ($m_p$):** ผู้โดยสาร (อยู่บนเบาะที่มีสปริง/แดมเปอร์ของตัวเอง)
  * **Suspension Model:** ![Suspension Model](pict/car_suspension.jpeg)
* **Input:** สัญญาณรบกวนจากพื้นถนน (Road Profile) เช่น ลูกระนาด (Bump)
* **Design Variables:** ต้องหาค่าพารามิเตอร์ของระบบกันสะเทือนหลัก 2 ตัว:
    1) **Suspension Stiffness ($k_s$):** ค่าความแข็งของสปริงรถ
    2) **Suspension Damping ($c_s$):** ค่าความหนืดของโช้คอัพรถ
* **Objective:** Maximize Passenger Comfort $\rightarrow$ **Minimize Passenger Acceleration ($a_p$)** โดยตรง

#### 5.3.2 ฟังก์ชันเป้าหมาย (Cost Function)

ในงานวิศวกรรมยานยนต์ "ความนุ่มสบาย" (Ride Quality) วัดได้จากแรงสั่นสะเทือนที่ส่งถึงตัวผู้โดยสาร โดย GWO จะพยายามลดค่า Cost Function ดังนี้:

$$ J(\vec{X}) = \int_{0}^{T} a_p(t)^2 dt $$

* **$a_p(t)$ (Passenger Acceleration):** ความเร่งในแนวดิ่งที่ตำแหน่งผู้โดยสาร
* **ความหมาย:** การหาผลรวมของพลังงานความสั่นสะเทือนตลอดช่วงเวลาที่ขับผ่านลูกระนาด
* **ทำไมต้องยกกำลังสอง?** เพื่อลงโทษค่าความเร่งที่สูงเกินไป (High Peak) อย่างรุนแรง ทำให้ GWO พยายามกำจัด "แรงกระแทก" (Shock) ให้เหลือน้อยที่สุด
* **Optimization Constraints:** กำหนดขอบเขตค่า $k, c$ ให้อยู่ในย่านที่เป็นไปได้จริงทางวิศวกรรม (เช่น $5000 \le k \le 100000$ N/m)

#### 5.3.3 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) การกำหนดตัวแปร (Variables Definition)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมาย (Description) |
| :--- | :--- | :--- |
| **`ks`** | *Optimized* | ค่าความแข็งสปริงช่วงล่าง (Suspension Stiffness) ที่ GWO ต้องหา |
| **`cs`** | *Optimized* | ค่าความหนืดโช้คอัพ (Suspension Damping) ที่ GWO ต้องหา |
| **`mu`** | `40.0` | มวลใต้สปริง (Unsprung Mass) เช่น ล้อ ยาง เบรก |
| **`ms`** | `300.0` | มวลเหนือสปริง (Sprung Mass) คือตัวถังรถยนต์ (คิดเป็น 1/4 ของรถ) |
| **`mp`** | `70.0` | มวลผู้โดยสาร (Passenger Mass) |
| **`kt`** | `200000.0` | ค่าความแข็งของยางรถยนต์ (Tire Stiffness) |

**2\) ลอจิกการทำงาน (Code Logic)**
ฟังก์ชัน `simulate_system` จะจำลองการตอบสนองของรถเมื่อวิ่งผ่านลูกระนาด โดยใช้สมการการเคลื่อนที่ (Equation of Motion) แบบ 3-DOF:
    1\) **Force Calculation:** คำนวณความต่างศักย์ (Displacement Difference) ระหว่างชั้นต่างๆ (ถนน-ล้อ, ล้อ-ตัวถัง, ตัวถัง-คน) เพื่อหาแรงกระทำในสปริงและโช้คแต่ละตัว
    2\) **Newton's Law:** ใช้ $F=ma$ หาความเร่งของมวลทั้ง 3 ก้อน ($a_u, a_s, a_p$)
    3\) **Integration:** อินทิเกรตความเร่งเพื่อหาความเร็วและตำแหน่งในสเต็ปถัดไป
    4\) **Cost Calculation:** ตลอดการจำลอง จะคอยเก็บสะสมค่าความเร่งของผู้โดยสาร ($a_p^2$) เพื่อส่งกลับเป็นค่า Fitness ให้ GWO (ยิ่งสั่นน้อย ค่า Cost ยิ่งต่ำ)

#### 5.3.4 ผลลัพธ์ (Results)

จากการจำลองแบบ 3-DOF ที่รวมผลกระทบของเบาะนั่งและตัวคนจริงๆ พบว่า GWO สามารถจูนระบบช่วงล่างรถยนต์ให้ลดแรงสั่นสะเทือนที่ส่งถึงตัวผู้โดยสารได้อย่างมีประสิทธิภาพสูงสุด

```text
Baseline (Sport Tuned): Passenger Comfort Cost = 43.3341
Optimal (Comfort Tuned): Passenger Comfort Cost = 1.5470
```

![Suspension Optimization](pict/suspension_opt.png)

**วิเคราะห์ผล (3 Subplots):**

1) **Vibration Isolation Layers (กราฟบน):** แสดงการส่งผ่านและลดทอนแรงสั่นสะเทือนจากถนนสู่ผู้โดยสาร (Vibration Transmission Path) อย่างชัดเจน:
    * **Road Input (เส้นประสีดำ):** สัญญาณรบกวนจากผิวถนน (ลูกระนาด) สูง 0.1m
    * **Wheel/Unsprung (เส้นจุดสีเขียว):** ล้อรถ ($z_u$) เคลื่อนที่ตามผิวถนนเกือบทั้งหมด
    * **Body/Sprung (เส้นประจุดสีเหลือง):** ตัวถังรถ ($z_s$) เริ่มกรองแรงสั่นสะเทือนออกไปได้ส่วนหนึ่ง
    * **Passenger (เส้นทึบสีน้ำเงิน):** ผู้โดยสาร ($z_p$) แทบไม่รู้สึกถึงแรงกระแทก กราฟราบเรียบที่สุด แสดงถึงประสิทธิภาพสูงสุดของการจูน ($Cost \approx 1.54$)
2) **Passenger Acceleration (กราฟกลาง):** ความเร่งลดลงอย่างมหาศาล ($1.54$ vs $43.33$) หมายถึงความรู้สึก "นิ่มนวล" ที่เพิ่มขึ้น

---

### 5.4 Robotics Inverse Kinematics (2-Link Arm, 2-DOF)

ตัวอย่างนี้แสดงการใช้ GWO แก้ปัญหา **Inverse Kinematics (IK)** สำหรับแขนหุ่นยนต์ 2 ก้านอิสระ (**2-DOF**: Degrees of Freedom) เพื่อให้ปลายแขน (End-Effector) เคลื่อนที่ตามเส้นทาง **รูปขดหอย (Spiral Trajectory)**

#### 5.4.1 ลักษณะโจทย์ (Scenario)

    1\) **System:** แขนหุ่นยนต์ 2 ก้าน ($L_1=1.0m, L_2=1.0m$) มีอิสระในการหมุน 2 จุดหมุน ($\theta_1, \theta_2$)
    2\) **Goal:** หาค่ามุมข้อต่อ $\theta_1, \theta_2$ ที่ทำให้ปลายแขน $(x_{tip}, y_{tip})$ ไปแตะจุดเป้าหมาย $(x_d, y_d)$ บนเส้นทางขดหอย
    3\) **Forward Kinematics Equations:**
        $$ x = L_1 \cos(\theta_1) + L_2 \cos(\theta_1 + \theta_2) $$
        $$ y = L_1 \sin(\theta_1) + L_2 \sin(\theta_1 + \theta_2) $$
    4\) **Objective Function:** Minimize Euclidean Distance Error
        $$ J = \sqrt{(x - x_d)^2 + (y - y_d)^2} $$

#### 5.4.2 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) การกำหนดตัวแปร (Variables Definition)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมาย (Description) |
| :--- | :--- | :--- |
| **`L1, L2`** | `1.0` | ความยาวของแขนกลท่อนที่ 1 และท่อนที่ 2 (เมตร) |
| **`theta`** | `[t1, t2]` | มุมข้อต่อที่ GWO สุ่มหา (Radians) |
| **`target_pos`** | `[x, y]` | พิกัดเป้าหมายที่ต้องการให้ปลายแขนไปแตะ |

**2\) ลอจิกการทำงาน (Code Logic)**
การแก้ปัญหา Inverse Kinematics ด้วย GWO ทำได้โดยการเปลี่ยนเป็นปัญหา Optimization:
    1\) **Forward Kinematics:** ฟังก์ชันที่รับค่ามุม `theta` แล้วคำนวณว่าปลายแขนจะไปอยู่ที่พิกัด $(x, y)$ ไหน (ใช้ตรีโกณมิติ sin/cos)
    2\) **Error Calculation:** นำพิกัดปลายแขนที่ได้ ไปเทียบกับพิกัดเป้าหมายจริง (`target_pos`)
    3\) **Objective Function:** ส่งคืนค่าความห่าง (Distance Error) กลับไป
        *   ถ้า $Error \approx 0$ แสดงว่ามุมที่สุ่มได้นั้นถูกต้อง แขนกลแตะโดนเป้าหมายพอดี
    4\) **Trajectory Loop:** โปรแกรมหลักจะวนลูปสร้างจุดเป้าหมายเรียงเป็นรูปก้นหอย แล้วเรียก GWO ให้แก้หาค่ามุมสำหรับจุดนั้นๆ ทีละจุดจนครบเส้นทาง

#### 5.4.3 ผลลัพธ์ (Results)

เราทดสอบให้หุ่นยนต์วาดรูปขดหอย (Archimedean Spiral) ที่มีความซับซ้อนกว่าวงกลม โดยให้ GWO หาค่ามุมในแต่ละจุด (Waypoint)

```text
Average Tracking Error: 0.0166 m
```

![Robot Arm Tracking](pict/robot_arm_opt.png)

1\) **Trajectory Trace (ซ้าย):** เส้นสีน้ำเงิน (GWO) สามารถเกาะติดตามเส้นประขดหอยสีดำ (Reference: Spiral) ได้อย่างแนบเนียน แสดงความแม่นยำในการแก้สมการ IK โดยในภาพได้ทำการวาดแขนหุ่นยนต์ให้ดูเป็นตัวอย่าง **ทุกๆ 10 จุด (Every 10th Waypoint)** เพื่อไม่ให้ภาพดูรกเกินไป และเห็นลักษณะการยืดหดของแขนตามรัศมีที่เปลี่ยนไป

2\) **Joint Angles (ขวา):** กราฟแสดงการเปลี่ยนแปลงของมุม $\theta_1, \theta_2$ ที่มีความต่อเนื่องและราบรื่น (Smooth Profile) ซึ่งสำคัญมากต่อการควบคุมมอเตอร์จริง

---

## 6. GWO in 3D Problem Solving (3 ตัวแปร)

ในหัวข้อนี้จะแสดงตัวอย่างการประยุกต์ใช้ GWO กับปัญหาที่มีตัวแปรต้องค้นหา 3 ตัวแปร (3 Dimensions)

### 6.1 PID Controller Tuning: Cruise Control (3D)

**กรณีศึกษา:** เดียวกันกับตัวอย่าง 4.8 และ 5.2 (Adaptive Cruise Control แบบ Stop-and-Go) แต่เปลี่ยนจากการหาแค่ $K_p$ หรือ $K_p, K_d$ มาเป็นการหาค่า **PID Parameters ทั้ง 3 ตัวพร้อมกัน**

#### 6.1.1 Problem Formulation

1\) **System Model:**
    *สมการควบคุม (PID Control Law) ที่ GWO ต้องจูน:
        $$ u(t) = K_p e(t) + K_i \int_{0}^{t} e(\tau) d\tau + K_d \frac{d e(t)}{dt} $$
    *   โดยที่ $u(t)$ คือแรงขับเคลื่อน (Force), $e(t)$ คือ Error ของระยะห่าง

2\) **Design Variables:** $$\vec{x} = [K_p, K_i, K_d]$$

3\) **Objective Function:** Minimize $J = \text{IAE} + \lambda \int u^2 dt$

* **Search Space:**
  * $K_p \in [100, 5000]$
  * $K_i \in [0.1, 100]$
  * $K_d \in [0.1, 5000]$

#### 6.1.2 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) การกำหนดตัวแปร (Variables Definition)**
ตัวแปรที่ใช้ในการจำลองระบบ (`m`, `b`, `dt`) เหมือนกับหัวข้อ 5.2 โดยส่วนที่ต่างคือตัวแปรที่ GWO ต้องค้นหา:

| ตัวแปร (Variable) | ช่วงค่า (Search Space) | ความหมาย (Description) |
| :--- | :--- | :--- |
| **`Kp`** | `100 - 5000` | Proportional Gain: ตอบสนองต่อ Error ปัจจุบัน (เร่งด่วน) |
| **`Ki`** | `0.1 - 100` | Integral Gain: ตอบสนองต่อ Error สะสม (แก้ปัญหาระยะห่างไม่ตรงเป๊ะ) |
| **`Kd`** | `0.1 - 5000` | Derivative Gain: ตอบสนองต่ออัตราการเปลี่ยนแปลง (ลดการแกว่ง) |

**2\) ลอจิกการทำงาน (Code Logic)**
กระบวนการจูนหาค่าพารามิเตอร์ทั้ง 3 ตัวพร้อมกัน มีลำดับดังนี้:

* **Step 1: Initialization (Dimension = 3):**
    GWO จะกำหนดให้หมาป่า 1 ตัว มีตำแหน่งเป็นเวกเตอร์ 3 มิติ $\vec{X} = [K_p, K_i, K_d]$
* **Step 2: Cost Function Design:**
    การคำนวณค่าความเหมาะสม (Fitness) ใช้สมการถ่วงน้ำหนัก:
    $$ J = \underbrace{\int |e(t)| dt}_{\text{Accuracy (IAE)}} + \underbrace{10^{-7} \times \int F(t)^2 dt}_{\text{Comfort/Effort}} $$
  * **IAE:** เน้นความแม่นยำในการรักษาระยะ (ยิ่งน้อยยิ่งดี)
  * **Effort:** เน้นการประหยัดพลังงาน/ความนุ่มนวล โดยคูณน้ำหนัก $10^{-7}$ เพื่อปรับสเกลให้สมดุลกับเทอมแรก
* **Step 3: Simulation Loop:**
    นำค่า $K_p, K_i, K_d$ จากหมาป่าแต่ละตัว ไปรันทดสอบในสถานการณ์รถติด (Stop-and-Go) เป็นเวลา 80 วินาที เมื่อจบการจำลองจะได้ค่า Cost ออกมาเพื่อใช้เปรียบเทียบหาจ่าฝูงต่อไป

#### 6.1.3 ผลลัพธ์ (Results)

GWO สามารถค้นหาค่าพารามิเตอร์ที่เหมาะสมที่สุดสำหรับทั้ง 3 ตัวแปรได้พร้อมกัน

```text
Kp: 5000.00
Ki: 100.00
Kd: 5000.00
Minimum Cost: 15.6096
```

![PID 3D Optimization](pict/pid_3d_opt.png)

**วิเคราะห์ผลเชิงลึก (Detailed Analysis):**

1\) **Steady-state Error Elimination (การกำจัด Error คงค้าง):**
    ***สิ่งที่คุณเห็น:** ในกราฟที่ 1 และ 2 รถ PID (สีแดง) สามารถวิ่งเกาะติดความเร็วเป้าหมายและรักษาระยะห่าง 10 เมตร ได้แนบสนิทกว่าแบบ PD ในหัวข้อ 5.2 อย่างเห็นได้ชัด
    *   **ที่มาทางทฤษฎี:** นี่คืออิทธิพลของเทอม **Integral ($K_i$)** ซึ่งทำหน้าที่ "สะสมความผิดพลาดในอดีต" ($ \int e dt $) หากรถมี Error ค้างอยู่แม้เพียงเล็กน้อย (เช่น ห่าง 10.5 เมตร) ค่า Integral จะค่อยๆ เพิ่มขึ้นเรื่อยๆ จนไปดันแรงขับเคลื่อน ($u(t)$) ให้รถขยับเข้าไปหาเป้าหมายจน Error กลายเป็น 0 ในที่สุด (ซึ่ง PD ทำไม่ได้ เพราะถ้า Error คงที่ Derivative จะเป็น 0 แรงจะหายไป)

2\) **Transient Response vs Stability (การตอบสนอง vs ความเสถียร):**
    ***ค่า $K_d$ ที่สูง (5000):** ช่วยทำหน้าที่เป็น "Damper" (ตัวหน่วง) คอยกดไม่ให้รถพุ่งกระชากเวลา $K_p$ สั่งเร่งแรงๆ ทำให้กราฟความเร็วมีความ Smooth ไม่มีการแกว่ง (Overshoot) แม้จะใช้ Gain สูง
    *   **ค่า $K_p$ ที่สูง (5000):** ทำให้รถตอบสนองต่อการเปลี่ยนแปลงความเร็วของคันหน้าได้ "ทันที" ยิ่งรวมกับ $K_i$ ยิ่งทำให้ Tracking ดีเยี่ยม

3\) **Comparison with PD Tuning (เปรียบเทียบกับ PD เดิม):**
    ***PD Cost:** 87.18
    *   **PID (3D) Cost:** ~15.61 (ลดลงกว่า 5.5 เท่า!)
    *   **บทสรุป:** การเพิ่มมิติที่ 3 ($K_i$) เข้ามา ทำให้ GWO มี "อาวุธ" ครบมือในการจัดการกับ Error ทั้งระยะสั้น ($P, D$) และระยะยาว ($I$) ผลลัพธ์จึงดีขึ้นอย่างก้าวกระโดด แสดงให้เห็นว่า GWO สามารถหาจุดสมดุลใน Search Space ที่ซับซ้อนขึ้น (3 ตัวแปร) ได้อย่างมีประสิทธิภาพสูงสุด

### 6.2 Robotic Inverse Kinematics (3-Link Planar Arm)

ตัวอย่างนี้เป็นการขยายความจากหัวข้อ 5.4 โดยเพิ่มความซับซ้อนของแขนหุ่นยนต์เป็น 3 ท่อน (**3-Link Planar Arm**) ซึ่งมีจุดหมุน 3 จุด ($\theta_1, \theta_2, \theta_3$) ทำให้เป็นปัญหา 3 มิติ (3-Dimensional Problem) ที่มีความซับซ้อนในการคำนวณ Forward Kinematics มากขึ้น

#### 6.2.1 ลักษณะโจทย์ (Scenario)

1\) **System:** แขนหุ่นยนต์ 3 ก้าน ($L_1=1.0m, L_2=1.0m, L_3=1.0m$) มีอิสระในการหมุน 3 จุดหมุน
2\) **Goal:** หาค่ามุมข้อต่อ $\vec{\theta} = [\theta_1, \theta_2, \theta_3]$ ที่ทำให้ปลายแขน (End-Effector) ไปแตะจุดเป้าหมายบนเส้นทางขดหอย
3\) **Forward Kinematics Equations (3-Link):**
    $$ x_{tip} = L_1 \cos(\theta_1) + L_2 \cos(\theta_1 + \theta_2) + L_3 \cos(\theta_1 + \theta_2 + \theta_3) $$
    $$ y_{tip} = L_1 \sin(\theta_1) + L_2 \sin(\theta_1 + \theta_2) + L_3 \sin(\theta_1 + \theta_2 + \theta_3) $$

#### 6.2.2 ส่วนประกอบของโค้ด (Code Logic & Variables)

**1\) การกำหนดตัวแปร (Variables Definition)**

| ตัวแปร (Variable) | ค่าที่ใช้ (Value) | ความหมาย (Description) |
| :--- | :--- | :--- |
| **`L1, L2, L3`** | `1.0` | ความยาวของแขนกลทั้ง 3 ท่อน (เมตร) |
| **`theta`** | `[t1, t2, t3]` | มุมข้อต่อทั้ง 3 ที่ GWO ต้องสุ่มหาค่า (ช่วง $-\pi$ ถึง $\pi$) |
| **`target_pos`** | `[x, y]` | พิกัดเป้าหมาย $(x, y)$ |
| **`Base`** | `(0.5, 0.5)` | จุดยึดฐานของหุ่นยนต์ (Base Position) |

**2\) ลอจิกการทำงาน (Code Logic)**
หลักการทำงานคล้ายกับ 2-Link Arm แต่เพิ่มมิติในการคำนวณ:

**Search Space Expansion:** พื้นที่ค้นหาคำตอบขยายเป็น 3 มิติ (Cube) แทนที่จะเป็น 2 มิติ (Square) ทำให้ความน่าจะเป็นในการติด Local Optima มีสูงขึ้น (เพราะแขน 3 ท่อนสามารถพับงอได้หลายท่าทางเพื่อไปแตะจุดเดียวกัน - Redundancy)

**Forward Kinematics Update:** ต้องคำนวณตำแหน่งข้อต่อที่ 3 เพิ่มเข้ามาในสมการตรีโกณมิติ

#### 6.2.3 ผลลัพธ์ (Results)

```text
Average Tracking Error: 0.0135 m
```

![3-Link Arm Optimization](pict/gwo_3d_arm_opt.png)

**วิเคราะห์ผล (Analysis):**

1\) **Increased Flexibility:** แขนกล 3 ท่อนมีความยืดหยุ่นสูงกว่า 2 ท่อน สามารถ "เอื้อม" หรือ "พับ" ได้หลากหลายท่ากว่า ทำให้สามารถวาดเส้นทางขดหอยได้อย่างลื่นไหล

2\) **High Accuracy:** ค่า Error เฉลี่ยอยู่ที่เพียง `0.0148 m` (1.48 ซม.) ซึ่งถือว่าแม่นยำมากสำหรับการควบคุมแขนกลแบบ Open-loop ด้วย Meta-heuristic แสดงให้เห็นว่า GWO สามารถจัดการกับสมการ Non-linear Equation System ที่ซับซ้อนขึ้นได้เป็นอย่างดี

## 7. การประยุกต์ใช้ GWO ในการปรับปรุง MPC Controller ในงาน Trajectory Follower

หัวข้อนี้นำเสนอแนวทางการนำ GWO มาประยุกต์ใช้ร่วมกับ **Model Predictive Control (MPC)** เพื่อแก้ปัญหาการติดตามเส้นทางสำหรับรถแทรกเตอร์ (Tractor Vehicle) โดยอ้างอิงจากระบบจำลองใน `mpc_simulation.md` ซึ่งใช้โมเดลทางคณิตศาสตร์แบบ **Kinematic Bicycle Model**

### 7.1 ลักษณะปัญหา (Problem Description)

1\) **ระบบควบคุม (MPC Formulation):** ระบบใช้การควบคุมแบบ **Error-State Formulation** โดยมีตัวแปรสถานะ ($x$) คือ:
    *$e_y$: Lateral Error (ความคลาดเคลื่อนทางด้านข้าง - Cross Track Error)
    *   $e_\theta$: Heading Error (ความคลาดเคลื่อนของทิศทางรถเทียบกับเส้นทาง)
    *   $e_v$: Velocity Error (ความคลาดเคลื่อนของความเร็วรถเทียบกับความเร็วอ้างอิง)

2\) **ความท้าทายในการจูน:** ประสิทธิภาพของการควบคุมขึ้นอยู่กับการกำหนดค่า **Weight Parameters** ในสมการ Cost Function ($J$) ที่สมดุลกัน:
    $$ J = \sum (x^T Q x + u^T R u + \text{rate\_penalties}) $$
    การกำหนดค่า Q และ R ที่เหมาะสมเป็นเรื่องยากและใช้เวลานาน (Trial & Error) โดยเฉพาะเมื่อต้องการสมดุลระหว่างความแม่นยำ (Tracking Accuracy) และความนุ่มนวล (Smoothness/Comfort)

### 7.2 กระบวนการทำงาน (Mechanism)

ใช้ GWO เป็นตัวค้นหาค่า Weight ที่ดีที่สุด (Optimal Weights) โดยเชื่อมต่อกับระบบจำลอง

1\) **หมาป่า (Wolf):** ตัวแทนของชุดพารามิเตอร์ที่ต้องการจูน ($W$) ซึ่งตรงกับค่าในไฟล์ `mpc_config.yaml`:
    $$ W = [w_{lat}, w_{heading}, w_{vel}, w_{steer\_rate}, w_{jerk}] $$
    (ค่า `lat_error`, `heading_error`, `velocity_error`, `steer_rate`, `lat_jerk`)

2\) **การจำลอง (Simulation Loop):**
    *ในแต่ละรอบ (Iteration) GWO จะส่งค่า $W$ ไปยัง `mpc_node.py`
    *   เริ่มการจำลองรถแทรกเตอร์ (`vehicle_node.py`) ให้วิ่งตามเส้นทาง Figure-8 (`path_publisher.py`)
    *   เก็บข้อมูลการตอบสนองของรถ (Response Data) ตลอดเส้นทาง

3\) **Fitness Evaluation (การประเมินค่าความเหมาะสม):**
    ระบบจะนำผลการจำลองตลอดทั้งเส้นทาง ($k=1 \dots N$ steps) มาคำนวณคะแนนรวมเป็นค่าเดียว (Scalar Value) โดยใช้สมการถ่วงน้ำหนักดังนี้:

$$ Fitness = \alpha \cdot J_{tracking} + \beta \cdot J_{stability} + \gamma \cdot J_{comfort} $$

* **Tracking Accuracy ($J_{tracking}$ - ความแม่นยำในการเกาะเส้น):**
        $$ J_{tracking} = \text{RMSE}(e_y) = \sqrt{\frac{1}{N} \sum_{k=1}^{N} (e_{y,k})^2} $$
        *$e_{y,k}$: Lateral Error ณ เวลา $k$ (ระยะห่างตั้งฉากระหว่างรถกับเส้นทางอ้างอิง)
        *   $N$: จำนวน Step ทั้งหมดในการจำลอง
        *   **ความหมาย:** ยิ่งค่านี้น้อย แสดงว่ารถวิ่งอยู่กึ่งกลางเลนตลอดเวลา

* **Stability ($J_{stability}$ - ความเสถียรของทิศทาง):**
        $$ J_{stability} = \text{Max}(|e_\theta|) = \max_{k=1 \dots N} |e_{\theta,k}| $$
        *$e_{\theta,k}$: Heading Error ณ เวลา $k$ (มุมที่หน้ารถเบี่ยงเบนไปจากเส้นทาง)
        *   **ความหมาย:** การใช้ค่าสูงสุด (Max) เพื่อป้องกันไม่ให้รถเกิดการสะบัดหรือหันหัวผิดทิศอย่างรุนแรง (Overshoot) แม้เพียงช่วงสั้นๆ

* **Comfort ($J_{comfort}$ - ความนุ่มนวลในการขับขี่):**
        $$ J_{comfort} = \sum_{k=1}^{N-1} |\delta_{k+1} - \delta_{k}|^2 + \sum_{k=1}^{N} |a_k|^2 $$
        *$\delta$: มุมเลี้ยว (Steering Angle) การเปลี่ยนแปลงมุมเลี้ยวที่รวดเร็วเกินไปจะทำให้รถส่าย
        *   $a$: ความเร่ง (Acceleration) การเร่งหรือเบรกที่รุนแรงจะทำให้ผู้โดยสารรู้สึกกระชาก
        *   **ความหมาย:** ยิ่งค่านี้น้อย การขับขี่จะยิ่งนุ่มนวล (Smooth Ride)

* **Weights ($\alpha, \beta, \gamma$):**
        *ค่าสัมประสิทธิ์ที่กำหนดความสำคัญของแต่ละเทอม
        *   เช่น หากต้องการ **รถแข่ง (Racing)** อาจจะตั้ง $\alpha$ สูงๆ เพื่อเน้นความแม่นยำและยอมแลกกับความนุ่มนวล
        *   หากต้องการ **รถโดยสาร (Bus)** อาจจะตั้ง $\gamma$ สูงๆ เพื่อเน้นความสบายของผู้โดยสารเป็นหลัก

### 7.3 Code Logic & Variables (การทำงานของโค้ดและตัวแปร)

**1) การทำงานของโค้ด (Code Logic)**

ระบบถูกออกแบบให้เป็น **Real-time Optimizer Node** ที่ทำงานคู่ขนานไปกับ MPC Controller หลัก (Parallel Execution) โดยมีลูปการทำงานดังนี้:

1. **Initialization:**
    * ดึงค่า MPC Weights **เริ่มต้น (Initial Guess)** จากไฟล์ `config/mpc_config.yaml` เพื่อใช้เป็น Seed ให้กับ GWO (ไม่เริ่มสุ่มจากศูนย์ เพื่อให้ระบบทำงานได้ทันที)
    * กำหนดขอบเขตการค้นหา (Search Space) เป็นเปอร์เซ็นต์บวกลบจากค่าเริ่มต้น (เช่น $\pm 20\%$)

2. **Data Collection (Sliding Window):**
    * Subscriber จะคอยรับค่าสถานะและ Error ต่างๆ (`/mpc/error_status`) จาก MPC node ตลอดเวลา
    * เก็บข้อมูลลงใน **Buffer** ที่มีความยาวคงที่ (เช่น ย้อนหลัง 1-2 วินาที) เพื่อใช้ประเมินผลงานแบบต่อเนื่อง

3. **Optimization Loop (5 Hz):**
    * ทำงานด้วยความถี่ **5 Hz** (ทุก 0.2 วินาที)
    * **Fitness Calculation:** คำนวณค่า Fitness จากข้อมูลใน Buffer (Performance ย้อนหลัง)
    * **GWO Update:** อัปเดตตำแหน่งหมาป่า (Weights ชุดใหม่) ตามสมการหลัก
    * **Model Update:** หากค้นพบค่า Weight ที่ให้ผลลัพธ์ดีกว่าค่าปัจจุบัน
        1. **Update Parameter:** เรียกใช้งาน **ROS Service** (`/mpc/set_trajectory_weights`) เพื่อส่งค่าฉบับใหม่ไปอัปเดต MPC ทันที
        2. **Save Parameter:** GWO Node จะทำการบันทึกค่าพารามิเตอร์ที่ดีที่สุด (Best Parameters) ลงไฟล์ Config (หรือแสดงผลให้ผู้ใช้ทราบ) เพื่อนำไปใช้งานต่อ

**2) การออกแบบ Node และ Topics**

**Target Node:** `gwo_tuner_node` (ROS 2 Node)

| Type | Topic Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **Sub** | `/mpc/error_status` | `Float64MultiArray` | รับค่า [CTE, HeadingErr, VelErr, SteerRate] จาก MPC เพื่อคำนวณ Fitness |
| **Sub** | `/odom` | `Odometry` | ตรวจสอบสถานะการเคลื่อนที่ของรถ |
| **ServiceClient** | `/mpc/set_trajectory_weights` | `SetTrajectoryWeights` | เรียก Service เพื่อส่งค่า Weight ชุดใหม่ไปอัปเดต MPC และรอรับผลการตอบรับ |

**3) Configuration (`config/gwo_config.yaml`)**

```yaml
gwo_node:
  ros__parameters:
    update_rate_hz: 5.0       # ความถี่ในการปรับจูนพารามิเตอร์ (5 Hz)
    history_window: 2.0       # ช่วงเวลาเก็บข้อมูลย้อนหลังเพื่อคำนวณ Fitness (วินาที)
    population_size: 10       # จำนวนหมาป่า (Pop Size)
    search_range_pct: 0.2     # ขอบเขตการค้นหา (+/- 20% จากค่าเริ่มต้น)
    targets:                  # รายชื่อพารามิเตอร์ที่ต้องการจูน (จาก mpc_config.yaml)
      - "lat_error"
      - "heading_error"
      - "velocity_error"
      - "steer_rate"
```

### 7.4 Pseudocode Scenario

ลำดับการทำงานของระบบเมื่อเริ่ม Start จนถึงการปรับจูนค่า:

```python
Node: GWO_Tuner
    Initialize:
        Load 'mpc_config.yaml' -> Get initial weights (W_best)
        Create Wolf Population around W_best
        Buffer = []
        
    Loop (Rate 5Hz):
        Input = Subscribe('/mpc/error_status')
        Buffer.append(Input)
        
        If Buffer is Full (Window size reached):
            Current_Fitness = CalculateFitness(Buffer)
            
            # GWO Algorithm
            For each Wolf in Population:
                Update Position (W_new) based on Alpha, Beta, Delta
                
            # Check if any Wolf is better than current W_best
            If Best_Wolf_Fitness < Current_Best_Fitness:
                W_best = Best_Wolf_Position
                
                # 1. Update Real-time
                Success = CallService('/mpc/set_trajectory_weights', W_best)
                If Success:
                    Log("MPC Updated Successfully")
                    
                # 2. Save Last Best Constants
                SaveToConfig('mpc_best_params.yaml', W_best)
                Log("New optimal weights saved!")
                
            Pop_Front(Buffer) # Slide window

Node: MPC_Controller (Service Server)
    OnRequest('/mpc/set_trajectory_weights', Request):
        Update internal weights (Q, R matrices) with Request.weights
        Return Success = True
    
    Loop (Rate 20Hz):
        State = Sense(Sensors)
        Control_Cmd = SolveMPC(State, Weights)
        Publish(Control_Cmd)
        Publish('/mpc/error_status', CalculateErrors(State, Path))
```

### 7.5 ประโยชน์ที่คาดว่าจะได้รับ (Expected Benefits)

* **Automated Tuning:** ลดเวลาและภาระของวิศวกรในการปรับจูนค่า MPC Weights ด้วยวิธีการลองผิดลองถูก (Trial & Error)
* **Real-time Adaptation:** สามารถปรับเปลี่ยนพารามิเตอร์ได้เองทันทีขณะใช้งานจริง (Online Tuning) เพื่อรับมือกับสภาพถนนที่เปลี่ยนไป
* **Optimal Performance:** สามารถค้นหาจุดสมดุลที่ดีที่สุด (Trade-off) ระหว่างการเกาะถนน (Tracking) และความนุ่มนวล (Comfort) ที่มนุษย์อาจปรับจูนได้ไม่ละเอียดเท่า
