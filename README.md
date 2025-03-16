### **📌 Let’s Write the README First**  
Since deleting files is annoying, let’s just **document everything properly** so future you doesn’t suffer.  

---

### **📄 README.md for SwanWidget**
This should be added to **your GitHub repo**:

```md
# SwanWidget 🦢

A draggable desktop swan that reacts when clicked, speaks, and quacks.

## 🚀 Features
- 🖱️ **Click**: Displays a random Johan de Witt quote.
- 🦢 **Double-click**: Makes the swan quack.
- 🎭 **Speech bubble**: The swan’s text appears slightly above it.
- 📌 **Draggable**: You can move the swan anywhere on your screen.

---

## 🛠️ Installation

### **1. Install Python & Pip**
Ensure you have **Python 3** installed. You can check with:
```sh
python3 --version
```
If pip isn’t installed, install it using:
```sh
python3 -m ensurepip --default-pip
```
If `pip3` is needed instead, try:
```sh
python3 -m ensurepip && python3 -m pip install --upgrade pip
```

---

### **2. Install Dependencies**
Navigate to your **SwanWidget folder** and install required Python packages:
```sh
pip3 install -r requirements.txt
```
OR manually install them:
```sh
pip3 install PyQt6 playsound pygame
```
---

### **3. Running the Swan**
Run this command in your **SwanWidget folder**:
```sh
python3 swan.py
```
OR, if you’ve set up an **Automator shortcut**, just double-click it.

---

## 📂 Dependencies (`requirements.txt` file)
To make installation easier, create a `requirements.txt` file with:
```
PyQt6
playsound==1.2.2
pygame
```
Now, installing dependencies is just:
```sh
pip3 install -r requirements.txt
```

---

## 🔧 Troubleshooting
### **🛑 If sound doesn’t work (quack missing)**
- Make sure the `quack.mp3` file is in the same directory as `swan.py`.
- Try running:
  ```sh
  pip3 install playsound==1.2.2
  ```
- If on Mac, ensure you have **pygame**, as some `playsound` versions don’t work on macOS.

### **🛑 If Python says module not found**
- Check if PyQt6 is installed:
  ```sh
  pip3 list | grep PyQt6
  ```
- If missing, reinstall:
  ```sh
  pip3 install PyQt6
  ```

### **🛑 If pip doesn’t work at all**
Try installing/updating pip:
```sh
python3 -m ensurepip --default-pip
python3 -m pip install --upgrade pip
```

---

## 🎯 Future Features
- 🖱️ **Right-click menu** (for clipboard history, settings, and more)
- 🎭 **Expression changes & animation**
- 🎮 **RPG-style interactions (feed the swan, pet the swan, etc.)**
- 🦢 **Web version** (so it works on iPad/iPhone)

---

## 🦢 Credits
SwanWidget is a project inspired by historical chaos and Johan de Witt’s unintentional **swan energy.**  

Quack responsibly.
```

---

### **📌 Now, Everything is Clear & Easy to Install**
- Future you (or anyone else) can **set up SwanWidget in seconds.**
- Everything is **documented properly**, so no frustration later.
- The **Troubleshooting section** saves debugging time.

---

### **📌 Next Steps**
1. **Add this README.md to your GitHub repo**.
2. **Create a `requirements.txt` file** if you haven’t already.
3. If needed, **run the pip installation fixes**.

Now, **future SwanWidget upgrades will be easier!** 🦢🚀
