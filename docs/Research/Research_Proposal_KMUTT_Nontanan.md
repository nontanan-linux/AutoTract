# ข้อเสนอโครงงานวิทยานิพนธ์ (Research Proposal)

**หัวข้อ**: การพัฒนาระบบควบคุมการติดตามเส้นทางแบบปรับตัวสำหรับรถลากจูงอัตโนมัติหลายพ่วง โดยใช้การหาค่าเหมาะที่สุดแบบเมตาเฮิวริสติกในระบบจำลอง CARLA
**(Development of an Adaptive Path Tracking Control System for a Multi-Trailer Autonomous Tow Truck using Metaheuristic Optimization in CARLA Simulator)**

**ผู้วิจัย**: นนทนันธ์ สมมาตร์ (Nontanan Sommat)
**อาจารย์ที่ปรึกษา**: ผศ. ดร. ดนัย เผ่าหฤหรรษ์ (Asst. Prof. Dr. Danai Phaoharuhansa)
**หลักสูตร**: วิศวกรรมยานยนต์ (A2TE), TAIST-Tokyo Tech
**สถาบัน**: มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าธนบุรี (KMUTT)

---

## CHAPTER I: INTRODUCTION (บทนำ)

### 1.1 Introduction and background (ที่มาและความสำคัญของปัญหา)

ในปัจจุบัน ระบบโลจิสติกส์อัตโนมัติมีความสำคัญอย่างยิ่งต่อการเพิ่มขีดความสามารถในการแข่งขันของอุตสาหกรรม การใช้งานรถลากจูงอัตโนมัติ (Autonomous Tow Truck) ร่วมกับรถพ่วงหลายชุด (Standard N-Trailer) เป็นโซลูชันที่มีประสิทธิภาพสูงในการขนส่งสินค้าปริมาณมากในพื้นที่จำกัด เช่น คลังสินค้าหรือโรงงานอัจฉริยะ อย่างไรก็ตาม ระบบดังกล่าวมีความท้าทายอย่างมากในด้านการควบคุม เนื่องจากข้อจำกัดทางจลนศาสตร์แบบ non-holonomic, โครงสร้างที่มีความเป็นเชิงเส้นต่ำ (non-linear dynamics) และความสัมพันธ์ของตำแหน่งแบบเรียกซ้ำ (recursive kinematics)

ปัญหาหลักที่พบคือ "Off-tracking" ซึ่งรถพ่วงส่วนท้ายจะไม่ได้เคลื่อนที่ตามรอยล้อของรถลากจูง และ "Jackknifing" หรือสภาวะรถพับซึ่งนำไปสู่ความไม่เสถียร นอกจากนี้ ในสภาวะการทำงานจริง มักเกิดความไม่แน่นอนของพารามิเตอร์ (Parameter Uncertainties) เช่น Steering Bias จากการสึกหรอของกลไก ซึ่งตัวควบคุมแบบมาตรฐานมักไม่สามารถชดเชยค่าเหล่านี้ได้ในเวลาจริง งานวิจัยนี้จึงมุ่งเน้นการพัฒนาระบบควบคุมแบบอแดปทีฟที่รวม NMPC และ NMHE เข้าด้วยกัน โดยใช้ GWO ในการปรับจูนพารามิเตอร์เพื่อให้เกิดความแม่นยำสูงสุด

### 1.2 Objective of the research (วัตถุประสงค์ของงานวิจัย)

1. เพื่อออกแบบและพัฒนาตัวควบคุมเชิงทำนายแบบไม่เชิงเส้น (NMPC) ที่สามารถจัดการข้อจำกัดทางกายภาพและป้องกันการพับงอ (Jackknifing) ได้อย่างมีประสิทธิภาพ
2. เพื่อพัฒนาระบบประมาณค่าสถานะและค่าไบแอสด้วยเทคนิค Moving Horizon Estimation (NMHE) สำหรับชดเชย Steering Bias แบบปรับตัว
3. เพื่อประยุกต์ใช้ขั้นตอนวิธี Grey Wolf Optimizer (GWO) ในการหาค่าพารามิเตอร์น้ำหนัก (Optimal Weight Tuning) อัตโนมัติ
4. เพื่อตรวจสอบความถูกต้องของระบบผ่านการจำลองที่มีความแม่นยำสูงใน CARLA Simulator ร่วมกับ ROS 2 และ Autoware Universe

### 1.3 Scope and limitation of the study (ขอบเขตและข้อจำกัดของการศึกษา)

1. มุ่งเน้นไปที่ระบบรถลากจูงพ่วงดร็อกบาร์ 4 ชุด (4-Drawbar Trailers)
2. ใช้แบบจำลองจลนศาสตร์ (Kinematic Model) เป็นพื้นฐานในการออกแบบตัวควบคุมหลัก
3. ทดสอบและจำลองผลบนระบบปฏิบัติการ ROS 2 (Humble) และ CARLA Simulator 0.9.15
4. พิจารณาข้อจำกัดความเร็วในช่วง 1.0 - 5.0 เมตรต่อวินาที ตามภารกิจในคลังสินค้า
5. งานวิจัยจำกัดอยู่ที่ระดับ Software-in-the-Loop (SiL) เท่านั้น

### 1.4 Expected benefits (ประโยชน์ที่คาดว่าจะได้รับ)

1. ได้ระบบควบคุมที่สามารถติดตามเส้นทางสำหรับรถพ่วง 4 ชุดได้อย่างแม่นยำ (Error < 10 cm)
2. ลดภาระในการปรับจูนพารามิเตอร์ตัวควบคุมด้วยการใช้ระบบอัตโนมัติ (GWO)
3. ได้องค์ความรู้ด้านการบูรณาการ NMPC/NMHE สำหรับระบบที่มีอิสระสูง (High-DoF)
4. สามารถนำผลงานวิจัยไปต่อยอดในอุตสาหกรรมโลจิสติกส์อัตโนมัติได้จริง

---

## CHAPTER II: LITERATURE REVIEWS (การทบทวนวรรณกรรม)

### 2.1 Multi-trailer kinematics and control

การวิจัยด้านจลนศาสตร์ของรถพ่วงแบบ N-Trailer มีมาอย่างยาวนาน โดยงานของ **Zhang et al. (2020)** นำเสนอแนวคิด Universal Control ผ่าน Hierarchical Layer (MPC + Control Allocation) ซึ่งสามารถลด Rollover Index ได้ถึง 36.5% นอกจากนี้ **Ye et al. (2025)** ได้พิสูจน์ความสำเร็จในการใช้ Distributed Cooperative Steering สำหรับรถบัส 3 ท่อน ซึ่งช่วยลด Lateral Deviation ได้มากกว่า 30% เมื่อเทียบกับ PID มาตรฐาน

### 2.2 Nonlinear Model Predictive Control (NMPC)

NMPC เป็นเครื่องมือที่ทรงพลังในการจัดการกับข้อจำกัด (Constraints) โดยตรง **Tian et al. (2025)** ได้นำเสนอการใช้กลยุทธ์ synergistic เพื่อป้องกัน Jackknifing โดยรวมระบบ Active Steering และ Torque Vectoring เข้าด้วยกัน ซึ่งช่วยลด Sideslip Angle ได้ถึง 84.26%

### 2.3 Nonlinear Moving Horizon Estimation (NMHE)

เพื่อเพิ่มความทนทานต่อสัญญาณรบกวน **Lee & Jeong (2024)** ได้แสดงให้เห็นว่าการใช้ MHE ร่วมกับ MPC ช่วยให้ระบบสามารถรักษา Path Tracking ได้แม้ในสภาวะที่มี Noise จากเซนเซอร์ตำแหน่งสูงถึง 0.5 เมตร

### 2.4 Grey Wolf Optimizer (GWO)

ขั้นตอนวิธี GWO ถูกนำมาใช้ในการหาค่าพารามิเตอร์ที่เหมาะสมที่สุด เนื่องจากมีความสมดุลระหว่างการสำรวจ (Exploration) และการใช้ประโยชน์ (Exploitation) ที่ดีกว่า GA หรือ PSO ในหลายกรณีศึกษา โดยเฉพาะการจูนค่าน้ำหนักในเมทริกซ์ $Q$ และ $R$ ของ MPC

---

## CHAPTER III: RESEARCH METHODOLOGY (ระเบียบวิธีวิจัย)

### 3.1 System Architecture

ระบบประกอบด้วย 4 ส่วนหลัก:

1. **Perception**: รับข้อมูลสถานะจาก CARLA ผ่าน ROS 2 Bridge
2. **Estimation (NMHE)**: ประมาณค่า Steering Bias และสถานะที่ไม่สามารถวัดได้
3. **Adaptive Layer (GWO)**: ปรับจูนน้ำหนักของ NMPC อัตโนมัติ
4. **Control (NMPC)**: คำนวณ Steering Angle และ Velocity

### 3.2 Full-Kinematic Recursive Model

แบบจำลองสำหรับรถพ่วง $k=1, \dots, 4$ กำหนดโดยสมการเรียกซ้ำ (Recursive Equations):

- **Dolly $k$**: $P_{2k-1} = H_k - L_{bar,k} [\cos \theta_{2k-1}, \sin \theta_{2k-1}]^T$
- **Axle $k$**: $P_{2k} = P_{2k-1} - L_{trl,k} [\cos \theta_{2k}, \sin \theta_{2k}]^T$
- **Next Hitch**: $H_{k+1} = P_{2k} - d_{h,k} [\cos \theta_{2k}, \sin \theta_{2k}]^T$

### 3.3 NMPC Controller Design

ฟังก์ชันต้นทุน (Cost Function):
$$J = \min_{u} \sum_{i=0}^{N_p} \|x_{t+i} - x_{ref,t+i}\|_Q^2 + \sum_{i=0}^{N_c-1} \|\Delta u_{t+i}\|_R^2$$
Subject to:

- $|\theta_k - \theta_{k-1}| < 45^\circ$ (Jackknifing Constraint)
- Steering Angle บวกลบ $30^\circ$

### 3.4 NMHE and Bias Compensation

ใช้หน้าต่างเวลา (Estimation Window) ขนาด $M$ เพื่อกรองสัญญาณรบกวนและระบุค่าคงที่ของระบบที่คลาดเคลื่อน

---

## CHAPTER IV: PRELIMINARY RESULTS (ผลการดำเนินงานเบื้องต้น)

### 4.1 Implementation Status

- ติดตั้งระบบจำลอง CARLA 0.9.15 และ ROS 2 Humble บน Ubuntu 22.04 LTS (100% Complete)
- พัฒนาและตรวจสอบความถูกต้องของแบบจำลองจลนศาสตร์ด้วยชุดโปรแกรม `tractor_odometry` (100% Complete)
- พัฒนาตัวควบคุม NMPC พื้นฐานด้วย CasADi และตรวจสอบผลใน Python (60% In Progress)

### 4.2 Validation Plan

ทดสอบผ่าน 3 รูปแบบเส้นทาง:

1. เส้นทางตรง (Straight Path)
2. เส้นทางโค้งรูปวงกลม (Circular Path)
3. เส้นทางรูปเลขแปด (Figure-Eight Path)

---

## CHAPTER V: CONCLUSION (สรุปผลและแผนการดำเนินงาน)

### 5.1 Conclusion

งานวิจัยนี้จะช่วยสร้างระบบควบคุมสำหรับรถพ่วงหลายส่วนที่ทำงานได้อย่างอัตโนมัติ มีเสถียรภาพ และทนทานต่อตัวแปรแวดล้อมที่เปลี่ยนแปลง

### 5.2 Research Timeline

- ม.ค. - ก.พ. 2026: พัฒนา Controller และ Estimator
- มี.ค. - เม.ย. 2026: บูรณาการ GWO ในระบบจำลอง
- พ.ค. - มิ.ย. 2026: ทดลองและวิเคราะห์ผล
- ก.ค. - ส.ค. 2026: เขียนวิทยานิพนธ์และสรุปผลงาน

---

## REFERENCES

1. Zhang, Y., Khajepour, A., & Ataei, M. (2020). A Universal and Reconfigurable Stability Control Methodology for Articulated Vehicles. *IEEE Transactions on Vehicular Technology*.
2. Ye, S., et al. (2025). Distributed Cooperative Steering Control for Three-Section Six-Axis Articulated Vehicles. *IEEE VPPC*.
3. Lee, T., & Jeong, Y. (2024). A Tube-Based Model Predictive Control for Path Tracking of Autonomous Articulated Vehicle. *Actuators*.
4. Tian, Y., et al. (2025). Synergistic Control Strategy for Enhanced Anti-Jackknifing Stability in Distributed-Drive Articulated Trucks. *IEEE TTE*.
5. Lei, T., et al. (2021). Modelling and Stability Analysis of Articulated Vehicles. *Applied Sciences*.
