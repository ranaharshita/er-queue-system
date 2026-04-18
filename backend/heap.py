# ─────────────────────────────────────────────────
# MAX HEAP - Priority Queue for ER Patients
# ─────────────────────────────────────────────────

class MaxHeap:

    def __init__(self):
        # This list stores all patients
        # Each patient is a dictionary like:
        # { "id": 1, "name": "Asha", "severity": "Critical", "arrival_time": ... }
        self.heap = []

    # ─────────────────────────────────────
    # Convert severity text to number
    # ─────────────────────────────────────
    def get_priority(self, severity):
        if severity == "Critical":
            return 3
        elif severity == "Moderate":
            return 2
        else:
            return 1  # Mild

    # ─────────────────────────────────────
    # Compare two patients
    # Returns True if patient A has higher
    # priority than patient B
    # ─────────────────────────────────────
    def has_higher_priority(self, a, b):
        priority_a = self.get_priority(a["severity"])
        priority_b = self.get_priority(b["severity"])

        if priority_a != priority_b:
            # Higher severity number wins
            return priority_a > priority_b
        else:
            # Same severity → earlier arrival wins
            return a["arrival_time"] < b["arrival_time"]

    # ─────────────────────────────────────
    # INSERT patient + Heapify Up
    # ─────────────────────────────────────
    def insert(self, patient):
        # Step 1: Add patient at the end
        self.heap.append(patient)

        # Step 2: Heapify Up
        self.heapify_up(len(self.heap) - 1)

    def heapify_up(self, index):
        # Keep moving up while current node has
        # higher priority than its parent
        while index > 0:
            parent = (index - 1) // 2

            if self.has_higher_priority(self.heap[index], self.heap[parent]):
                # Swap child with parent
                self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
                # Move up
                index = parent
            else:
                # Heap property satisfied, stop
                break

    # ─────────────────────────────────────
    # REMOVE top patient + Heapify Down
    # ─────────────────────────────────────
    def remove_max(self):
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        # Step 1: Save the top patient (highest priority)
        top_patient = self.heap[0]

        # Step 2: Move last patient to top
        self.heap[0] = self.heap.pop()

        # Step 3: Heapify Down to fix the heap
        self.heapify_down(0)

        return top_patient

    def heapify_down(self, index):
        size = len(self.heap)

        while True:
            left    = (2 * index) + 1   # left child
            right   = (2 * index) + 2   # right child
            largest = index             # assume current is largest

            # Check if left child has higher priority
            if left < size and self.has_higher_priority(self.heap[left], self.heap[largest]):
                largest = left

            # Check if right child has higher priority
            if right < size and self.has_higher_priority(self.heap[right], self.heap[largest]):
                largest = right

            if largest != index:
                # Swap with the larger child
                self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
                index = largest
            else:
                # Heap property satisfied, stop
                break

    # ─────────────────────────────────────
    # VIEW the heap as a sorted list
    # (for dashboard display)
    # ─────────────────────────────────────
    def get_sorted_queue(self):
        # We don't destroy the heap
        # We just return a sorted copy for display
        import copy
        temp_heap = MaxHeap()
        temp_heap.heap = copy.deepcopy(self.heap)

        sorted_list = []
        while len(temp_heap.heap) > 0:
            sorted_list.append(temp_heap.remove_max())

        return sorted_list

    # ─────────────────────────────────────
    # PEEK - see top patient without removing
    # ─────────────────────────────────────
    def peek(self):
        if self.heap:
            return self.heap[0]
        return None

    # ─────────────────────────────────────
    # SIZE of the heap
    # ─────────────────────────────────────
    def size(self):
        return len(self.heap)


# ─────────────────────────────────────
# One global heap for the whole server
# ─────────────────────────────────────
# ─────────────────────────────────────
    # UPDATE patient severity in heap
    # Used for priority aging
    # ─────────────────────────────────────
    def update_severity(self, patient_id, new_severity):
        # Find the patient in heap by id
        for i in range(len(self.heap)):
            if self.heap[i]["id"] == patient_id:
                old_severity = self.heap[i]["severity"]
                self.heap[i]["severity"] = new_severity

                print(f"Upgraded {self.heap[i]['name']} from {old_severity} to {new_severity}")

                # Re-heapify up from this position
                # because priority increased
                self.heapify_up(i)
                return True
        return False
er_heap = MaxHeap()