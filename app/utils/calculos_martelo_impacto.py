import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import copy

def martelo_impacto_resposta_tempo(f, c, k, m, t):
    """Resposta de sistema massa-mola-amortecedor"""
    if m <= 0: m = 1e-6
    if k <= 0: k = 1e-6

    w_n = np.sqrt(k / m)
    zeta = c / (2 * m * w_n)
    arg = 1 - zeta**2
    w_d = w_n * np.sqrt(arg) if arg > 0 else 0.0

    if w_d == 0:
        x = 0.0
    else:
        x = f * (np.exp(-zeta * w_n * t) / (m * w_d)) * np.sin(w_d * t)

    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return x


def calcular_r2(y_true, y_pred):
    """R² simples"""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot != 0 else 0


def analise_inversa_martelo_impacto(m, c, f, k, dano):
    """Analise inversa do martelo"""
    x_values = np.linspace(0, 5, 200)
    y_sem_dano = [martelo_impacto_resposta_tempo(f, c, k, m, t) for t in x_values]
    y_com_dano = [martelo_impacto_resposta_tempo(f, c, k*(1-dano), m, t) for t in x_values]

    k_novo = np.linspace(k*0.4, k*1.2, 100)
    kk = k
    r2_final = float('-inf')
    y = None

    for k_val in k_novo:
        y_new = [martelo_impacto_resposta_tempo(f, c, k_val, m, t) for t in x_values]
        r2 = calcular_r2(y_com_dano, y_new)
        if r2 > r2_final:
            kk = k_val
            r2_final = r2
            y = copy.deepcopy(y_new)

    if y is None:
        y = y_com_dano
        kk = k

    # Criar figura
    fig, ax = plt.subplots()
    ax.plot(x_values, y_sem_dano, label='s/ dano', color='green')
    ax.plot(x_values, y_com_dano, label='c/ dano', color='red')
    ax.plot(x_values, y, label=f'Identificação k={kk:.2f}, r²={r2_final:.4f}', linestyle='--', color='blue')
    ax.set_xlabel('t (s)')
    ax.set_ylabel('x (m)')
    ax.grid(True)
    ax.legend()
    plt.close(fig)

    return fig, kk, y


def martelo_impacto_gif(y_values):
    """Gera GIF a partir de y_values"""
    frames = []
    x_values = np.linspace(0, 5, len(y_values))
    for i in range(1, len(x_values)+1, 5):
        fig, ax = plt.subplots()
        ax.plot(x_values[:i], y_values[:i], color='blue')
        ax.set_xlim(0, 5)
        y_min, y_max = np.min(y_values), np.max(y_values)
        if not np.isfinite(y_min) or not np.isfinite(y_max):
            y_min, y_max = 0, 1
        ax.set_ylim(y_min, y_max)
        ax.grid(True)

        fig.canvas.draw()  # renderiza

        w, h = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)  # RGBA
        pil_img = Image.fromarray(buf[:, :, :3])  # apenas RGB
        frames.append(pil_img)
        plt.close(fig)
    return frames
