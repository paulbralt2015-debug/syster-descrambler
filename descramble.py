import sys, cv2, numpy as np
from scipy.spatial.distance import cdist

def order_lines(gray, k=8):
    H, W = gray.shape
    g = gray.astype(np.float32)
    D = cdist(g, g, 'cityblock') / W
    np.fill_diagonal(D, np.inf)

    # candidats : les k lignes les plus proches de chaque ligne
    nn = np.argsort(D, axis=1)[:, :k]
    edges = {(min(i, j), max(i, j)) for i in range(H) for j in nn[i]}
    edges = sorted(edges, key=lambda e: D[e])

    parent = list(range(H))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    deg = np.zeros(H, int)
    adj = [[] for _ in range(H)]
    def link(a, b):
        adj[a].append(b); adj[b].append(a)
        deg[a] += 1; deg[b] += 1
        parent[find(a)] = find(b)

    # assemblage glouton des meilleures paires
    for a, b in edges:
        if deg[a] < 2 and deg[b] < 2 and find(a) != find(b):
            link(a, b)

    # relier les fragments restants
    while True:
        ends = np.array([n for n in range(H) if deg[n] < 2])
        comp = np.array([find(n) for n in ends])
        if len(set(comp)) == 1:
            break
        sub = D[np.ix_(ends, ends)].copy()
        sub[comp[:, None] == comp[None, :]] = np.inf
        a, b = np.unravel_index(np.argmin(sub), sub.shape)
        link(int(ends[a]), int(ends[b]))

    # parcourir le chemin
    start = next(n for n in range(H) if deg[n] < 2)
    order, prev, cur = [start], -1, start
    while len(order) < H:
        nxt = [n for n in adj[cur] if n != prev]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        order.append(cur)
    return np.array(order)

def main(src, dst, flip=False):
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    prev_out = None
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        order = order_lines(gray)
        if prev_out is not None:
            # choisir le sens (haut/bas) le plus proche de l'image précédente
            a = np.abs(frame[order].astype(int) - prev_out).mean()
            b = np.abs(frame[order[::-1]].astype(int) - prev_out).mean()
            if b < a:
                order = order[::-1]
        elif flip:
            order = order[::-1]
        res = frame[order]
        prev_out = res.astype(int)
        out.write(res)
        n += 1
        if n % 25 == 0:
            print(f"{n} images traitées")
    cap.release(); out.release()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : descramble.py entree.mp4 sortie.mp4 [--flip]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], flip=("--flip" in sys.argv))
