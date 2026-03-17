# Restaurant Priority System

## How It Works

The automated availability checker now respects your custom priority order!

### 1. Set Your Priority Order

Open the priority editor:
```bash
open restaurants/priority-editor.html
```

**Or drag this file into your browser.**

### 2. Drag to Reorder

- Each section (Haven't Been Yet, Would Return) can be reordered independently
- Drag the **☰ handle** to move restaurants up/down
- Priority numbers (#1, #2, #3...) update automatically
- Higher priority = checked first during automation

### 3. Save Your Order

Click **💾 Save Order** button:
- Saves to browser localStorage (persistent)
- Downloads `restaurant-priority.json` file
- This JSON file tells the Python script your preferred order

### 4. Place the JSON File

After saving, a file downloads: `restaurant-priority.json`

**Move it to the restaurants folder:**
```bash
mv ~/Downloads/restaurant-priority.json restaurants/
```

### 5. Run Automation

Now when you run availability checks:
```bash
python3 restaurants/auto_check.py 5
```

It will check restaurants **in your custom priority order!**

## Benefits

✅ **Your favorites get checked first**  
✅ **Visual, drag-and-drop interface**  
✅ **Easy to reorganize anytime**  
✅ **Automation respects your preferences**  

## Example Use Cases

**Prioritize new experiences:**
1. Move "Haven't Been Yet" favorites to top
2. Push familiar spots lower
3. Save order
4. Automation finds new places first

**Date night mode:**
1. Reorder to put romantic spots at top
2. Save as separate priority file
3. Use for date night searches

**Special occasion:**
1. Temporarily boost "Special Occasion" section
2. Run availability check
3. Reset to default after booking

## Resetting

**Reset to default order:**
- Click **↺ Reset to Default** in the editor
- Or delete `restaurant-priority.json` file

**The script will fall back to default order if no priority file exists.**

## Tips

- **Drag multiple at once:** Shift priority by moving one restaurant way up/down
- **Section-specific:** Each section maintains its own order
- **Re-export anytime:** Click 📥 Export JSON to download current order
- **Keep backups:** Save different priority files for different situations

---

**Priority system active!** Your automation now checks restaurants in the order YOU define. 🦁
