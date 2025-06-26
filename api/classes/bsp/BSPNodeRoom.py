import random
class BSPNode:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.left = None
        self.right = None
        self.room = None

    def split(self, min_size, max_size):
        nodes = [self]
        did_split = True

        while did_split:
            did_split = False
            new_nodes = []
            for node in nodes:
                if node.left or node.right:
                    new_nodes.append(node)
                    continue
                if node.w > max_size or node.h > max_size or random.random() > 0.5:
                    if node._split(min_size):
                        new_nodes.append(node.left)
                        new_nodes.append(node.right)
                        did_split = True
                    else:
                        new_nodes.append(node)
                else:
                    new_nodes.append(node)
            nodes = new_nodes
        return [n for n in nodes if not n.left and not n.right]

    def _split(self, min_size):
        horizontal = random.choice([True, False])
        if self.w > self.h and self.w / self.h >= 1.25:
            horizontal = False
        elif self.h > self.w and self.h / self.w >= 1.25:
            horizontal = True

        max_split = (self.h if horizontal else self.w) - min_size
        if max_split <= min_size:
            return False

        split = random.randint(min_size, max_split)
        if horizontal:
            self.left = BSPNode(self.x, self.y, self.w, split)
            self.right = BSPNode(self.x, self.y + split, self.w, self.h - split)
        else:
            self.left = BSPNode(self.x, self.y, split, self.h)
            self.right = BSPNode(self.x + split, self.y, self.w - split, self.h)
        return True

    def create_room(self):
        room_margin = 2
        room_w = random.randint(3, self.w - room_margin)
        room_h = random.randint(3, self.h - room_margin)
        room_x = random.randint(self.x + 1, self.x + self.w - room_w - 1)
        room_y = random.randint(self.y + 1, self.y + self.h - room_h - 1)
        self.room = Room(room_x, room_y, room_w, room_h)
        return self.room


class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)
