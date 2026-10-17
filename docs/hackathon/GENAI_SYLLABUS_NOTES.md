# Gen AI course: syllabus study notes (Units 1–5)

Revision notes for the Third Year Computer Engineering Gen AI course, the course this hackathon belongs to.
Each unit has the core ideas, the formulas worth writing, and a **"In ResQPulse"** line so you can link theory to the project in the viva.
The syllabus image showed Units 1–5; if there is a Unit 6, add it here.

---

## Syllabus terms used in ResQPulse (with where to point)

Every term below is something the project **actually does**. The exact values come from `scripts/train_classifier.py`
(as run in `notebooks/classifier-notebook.ipynb`), `notebooks/flan-t5-train.ipynb`, `src/models/` and `scripts/`.
Use the "Where" column if an examiner asks you to show it.

### Unit 1: Neural network basics

| Term | How ResQPulse uses it | Where |
|---|---|---|
| **Artificial neural network** | All three models (DistilBERT, Flan-T5, Whisper) are deep neural networks | `src/models/`, `src/asr/` |
| **Deep learning revolution** (data + GPUs + pre-training) | Trained on free **Kaggle T4 GPUs**; started from models pre-trained on huge corpora | Kaggle notebooks |
| **Transfer learning** | Fine-tuned pre-trained `distilbert-base-uncased` and `google/flan-t5-base` on our 9,551 rows | `notebooks/` |
| **Fine-tuning vs feature extraction** | **Full fine-tuning**: all DistilBERT and Flan-T5 weights were updated, nothing frozen | `train_classifier.py` |
| **Zero-shot use of a pre-trained model** | Whisper small.en used **as is**, not trained by us | `src/asr/whisper.py` |
| **Neuron, weights, bias** | Our two heads are linear layers `W·x + b` on top of DistilBERT | `src/models/two_head.py` |
| **Activation functions** | **Softmax** (type probabilities), **sigmoid** (severity squashed to 0–1, then scaled to 1–5), **GELU** inside DistilBERT, **gated-GELU** in Flan-T5's feed-forward layers | `two_head.py` |
| **Steps in training** | Clean data → split train/val/test → tokenise → forward pass → loss → backprop → AdamW update → evaluate each epoch → test on held-out sets | `train_classifier.py` |
| **Train / validation / test split** | Train 9,551; val for monitoring; tests: 107 synthetic, 7,755 real tweets, 144-report gold set | `scripts/make_splits.py` |
| **Loss function: cross-entropy** | Incident-type head (8 classes); Flan-T5 token-level cross-entropy | `two_head.py`, Flan notebook |
| **Loss function: MSE** | Severity head, **masked** so rows without a severity label add zero | `two_head_loss()` |
| **Multi-task learning** (two heads, one body) | One DistilBERT encoder feeds both the type head and the severity head; loss = CE + MSE | `two_head.py` |
| **Optimiser: AdamW** | `torch.optim.AdamW` for DistilBERT; the Seq2Seq trainer's AdamW for Flan-T5 | both |
| **Learning rate** | 2e-5 (DistilBERT), 1e-4 (Flan-T5) | both |
| **Learning-rate warmup + linear decay** | 6% warmup then linear decay (DistilBERT); 10 warmup steps (Flan-T5) | `get_linear_schedule_with_warmup` |
| **Weight decay (L2 regularisation)** | 0.01, not applied to biases and LayerNorm weights | both |
| **Dropout** | 0.1 on the [CLS] vector before the heads | `two_head.py` |
| **Epochs** | 3 (DistilBERT), 5 (Flan-T5) | both |
| **Batch size, gradient accumulation** | 32 (DistilBERT); 4 × 4 accumulation = effective 16 (Flan-T5) | both |
| **Gradient clipping** (against exploding gradients) | Max norm 1.0 | `train_classifier.py` |
| **Mixed precision (fp16)** | Used on GPU for DistilBERT; Flan-T5 kept in **fp32** because T5 is unstable in fp16 | both |
| **Random seed** (reproducibility) | 42 everywhere | both |
| **Parameters** | About 66M (DistilBERT) + our heads; about 250M (Flan-T5); about 244M (Whisper small) | — |
| **Hyperparameters** | Learning rate, epochs, batch size, max length (128 / 256 / 160 tokens), warmup, weight decay, dropout, beam size (4, retry 6), logistic-regression C (tuned on validation), duplicate threshold 0.75, 4× repeat of synthetic rows, 1,200-per-class cap | — |
| **Hyperparameter tuning on a validation set** | Baseline's regularisation strength C chosen by validation macro-F1 | `scripts/baseline_tfidf_lr.py` |
| **Backpropagation** | PyTorch autograd computes every gradient (`loss.backward()`) | `train_classifier.py` |
| **Overfitting control** | Dropout, weight decay, few epochs, a separate gold set never used for training or tuning | — |

### Unit 2: Foundational architectures

| Term | How ResQPulse uses it | Where |
|---|---|---|
| **MLP / fully connected layers** | Type head (768 → 8) and severity head (768 → 1); the feed-forward block in every Transformer layer is a 2-layer MLP | `two_head.py` |
| **RNN (why not)** | We chose a Transformer over an RNN/LSTM because it is parallel, handles long-range context, and comes pre-trained | Design choice |
| **Linear baseline** (comparison model) | TF-IDF (word 1–2-grams + character 2–5-grams) + logistic regression, to prove the network adds value | `scripts/baseline_tfidf_lr.py` |

### Unit 3: Advanced and generative AI

| Term | How ResQPulse uses it | Where |
|---|---|---|
| **Generative AI model** | **Flan-T5 generates** the alert fields and summary as text; **Whisper generates** a transcript from audio | `src/models/generator.py` |
| **Discriminative vs generative** | DistilBERT is discriminative (classifies); Flan-T5 and Whisper are generative | — |
| **Generative AI for data augmentation / synthetic data** | Claude (a generative LLM) wrote the **710 call-style training reports** and pre-labelled the gold set (offline, never at run time) | `data/`, `scripts/validate_synthetic.py` |
| **Encoder-decoder architecture** | Flan-T5 and Whisper are encoder-decoders | — |
| **Residual (skip) connections** | Inside every Transformer layer; also added in **attention rollout** | DistilBERT, `src/models/classifier.py` |

### Unit 4: Encoders, Transformers and attention (the core)

| Term | How ResQPulse uses it | Where |
|---|---|---|
| **Transformer** | All three models are Transformers | — |
| **Encoder-only Transformer** | DistilBERT (6 layers, 12 heads, hidden size 768) | classifier |
| **Encoder-decoder Transformer** | Flan-T5-base and Whisper | generator, ASR |
| **Self-attention, Q/K/V, softmax(QKᵀ/√dₖ)V** | Inside every DistilBERT layer; we read its attention weights with `output_attentions=True` | `src/models/classifier.py` |
| **Multi-head attention** | 12 heads per layer in DistilBERT; heads are averaged before rollout | `attention_rollout()` |
| **Cross-attention** | Flan-T5's decoder attends to the report; Whisper's decoder attends to the audio | — |
| **Masked (causal) attention** | Flan-T5 and Whisper decoders generate one token at a time, seeing only earlier tokens | — |
| **Attention rollout (explainability)** | Attention multiplied across all 6 layers, with the identity added for the residual, to get each word's influence on [CLS]; shown as the **yellow heatmap** | `attention_rollout()`, Attention Heatmap screen |
| **[CLS] token representation** | The [CLS] vector from the last layer feeds both heads | `two_head.py` |
| **Positional embeddings** | Learned in DistilBERT; relative position biases in T5 | — |
| **Layer normalisation** | In every Transformer block; excluded from weight decay | `train_classifier.py` |
| **Tokenisation (subwords)** | WordPiece (DistilBERT), SentencePiece (T5); **word pieces merged back into words** for the heatmap | `words_with_scores()` |
| **Truncation / max sequence length** | 128 tokens (DistilBERT), 256 input + 160 output (Flan-T5) | both |
| **Knowledge distillation** | DistilBERT itself is a distilled BERT (about 40% smaller, 60% faster) | — |
| **Instruction tuning** | Flan-T5 is T5 instruction-tuned by Google; we added a task prefix `extract alert:` | `src/data/flan.py` |
| **Seq2seq fine-tuning, teacher forcing** | Flan-T5 trained with `Seq2SeqTrainer` on input → target pairs | Flan notebook |
| **Decoding: beam search** | 4 beams, retried with 6 if the output is incomplete | `generator.py` |
| **Structured output from a generator** | Flat `key: value \| …` format (T5 has no `{}` tokens), parsed to JSON, with a rule fallback | `src/data/flan.py`, `generator.py` |
| **Sentence embeddings (encoder output as a vector)** | `all-MiniLM-L6-v2` turns each report into a vector; cosine similarity > 0.75 = possible duplicate | `src/services/deduplication.py` |

### Unit 5: Python and data for generative AI

| Term | How ResQPulse uses it | Where |
|---|---|---|
| **Python ML stack** | Python 3, NumPy, Pandas, scikit-learn, **PyTorch**, Hugging Face Transformers, FastAPI, Streamlit | `requirements.txt` |
| **Preprocessing and cleaning text** | Strip URLs, @mentions, leading RT and `#`; unescape HTML; collapse spaces; map labels to a fixed schema; drop too-short rows | `src/data/clean.py`, `scripts/build_public.py` |
| **De-duplication and data leakage** | Duplicate tweets (retweets, copies) dropped after normalising, keeping the training copy, so no test tweet also appears in training | `scripts/build_public.py` |
| **Class imbalance handling** | Cap of 1,200 per class; synthetic rows repeated 4× | `make_splits.py` |
| **Data validation** | Every phrase a synthetic report claims must appear word for word (710 of 711 kept) | `scripts/validate_synthetic.py` |
| **Audio preprocessing** | ffmpeg decode (via pydub), resample to 16 kHz mono, voice-activity detection (min silence 500 ms) | `src/asr/whisper.py` |
| **Quantisation** | Whisper run in **int8** for fast CPU inference | `src/asr/whisper.py` |
| **Visualising data and results** | Confusion matrices, class-count tables, attention heatmap, metrics screen | `reports/`, dashboard |
| **Eager execution** | PyTorch runs eagerly (like TF2's default), with `torch.no_grad()` for inference | `src/models/` |
| **Evaluation metrics** | Precision, recall, F1 (macro), accuracy, MSE, RMSE, MAE, ROUGE-L, word error rate | `src/eval/metrics.py`, `scripts/evaluate.py` |

### Syllabus terms we did *not* use (and the one-line answer)

| Term | Honest answer |
|---|---|
| **CNN** | Not used; our input is text and audio sequences, where Transformers are stronger. Whisper's encoder does begin with two small convolution layers over the audio spectrogram. |
| **RNN / LSTM** | Not used; replaced by Transformers for parallelism and long-range context. |
| **GAN** | Not used; we generated synthetic text with an LLM instead. A conditional GAN could generate rare-class reports in future. |
| **VAE** | Not used; a VAE's reconstruction error could flag unusual reports (anomaly detection) as future work. |
| **TensorFlow 2 / Keras** | We used **PyTorch**, which plays the same role: eager tensors, autograd ≈ GradientTape, `DataLoader` ≈ `tf.data`, `torch.compile` ≈ `tf.function`. |

---

## Unit 1: Introduction to Neural Networks

### 1.1 History (know the timeline)
| Year | Milestone | Why it matters |
|---|---|---|
| 1943 | McCulloch & Pitts neuron | First mathematical model of a neuron (weighted sum + threshold) |
| 1958 | Rosenblatt's **Perceptron** | First learning rule; learns a linear boundary |
| 1969 | Minsky & Papert, *Perceptrons* | A single perceptron cannot learn XOR → first "AI winter" |
| 1986 | Rumelhart, Hinton, Williams: **backpropagation** | Made training multi-layer networks practical |
| 1989–98 | LeCun's **CNN (LeNet)** | Convolutions for digit recognition |
| 1997 | Hochreiter & Schmidhuber: **LSTM** | Fixed vanishing gradients in RNNs |
| 2006 | Hinton: deep belief nets | Restarted interest in "deep" learning |
| 2012 | **AlexNet** wins ImageNet | GPUs + ReLU + dropout + big data → the deep learning revolution |
| 2014 | **GANs** (Goodfellow), **VAE** (Kingma & Welling, 2013), seq2seq | Generative models take off |
| 2017 | **Transformer** ("Attention Is All You Need") | Attention replaces recurrence |
| 2018+ | BERT, GPT, T5, then LLMs, diffusion models | Pre-training + fine-tuning becomes the default |

### 1.2 The deep learning revolution: why it happened around 2012
1. **Data:** large labelled datasets such as ImageNet.
2. **Compute:** GPUs make matrix multiplications fast.
3. **Algorithms:** ReLU (fewer vanishing gradients), dropout, better initialisation, batch normalisation, Adam.
4. **Software:** frameworks such as TensorFlow and PyTorch, with automatic differentiation.

### 1.3 Transfer learning
- **Idea:** reuse a model trained on a big general task (pre-training), then adapt it to your task (fine-tuning).
- **Two styles:**
  - **Feature extraction:** freeze the pre-trained layers and train only a new head.
  - **Fine-tuning:** unfreeze some or all layers and train with a small learning rate.
- **Why:** you need far less data and compute, and get better accuracy on small datasets.
- **In ResQPulse:** we fine-tuned pre-trained **DistilBERT** and **Flan-T5** on about 9,500 examples instead of training from scratch, and used pre-trained **Whisper** as it is (zero-shot).

### 1.4 Structure of an artificial neural network
- **Neuron:** `z = w·x + b`, then `a = f(z)`, where *f* is an activation.
- **Layers:** input layer → one or more **hidden layers** → output layer. Fully connected = every neuron connects to every neuron in the next layer.
- **Activation functions** (they add non-linearity; without them, many layers collapse into one linear layer):

| Function | Formula | Use |
|---|---|---|
| Sigmoid | σ(z) = 1 / (1 + e^(−z)) | Binary output; saturates, so gradients vanish |
| Tanh | (e^z − e^(−z)) / (e^z + e^(−z)) | Zero-centred, range −1 to 1 |
| ReLU | max(0, z) | Default for hidden layers; fast; can "die" |
| Leaky ReLU | max(αz, z) | Fixes dying ReLU |
| Softmax | e^(z_i) / Σ e^(z_j) | Multi-class probabilities |
| GELU | z·Φ(z) | Used in Transformers (BERT, GPT) |

### 1.5 Steps in training a neural network
1. **Prepare the data:** clean, split into train / validation / test, normalise or tokenise.
2. **Define the architecture:** layers, sizes, activations.
3. **Initialise the weights:** small random values, e.g. Xavier/Glorot or He.
4. **Forward pass:** compute predictions.
5. **Compute the loss:** e.g. cross-entropy or MSE.
6. **Backward pass:** backpropagation computes the gradients.
7. **Update the weights:** with an optimiser, `w ← w − η · ∂L/∂w`.
8. **Repeat** for many epochs. Watch the validation loss and stop early if it rises (overfitting).
9. **Evaluate** on the held-out test set.

- **Loss functions:**
  - **MSE** = (1/n) Σ (y − ŷ)² for regression.
  - **Cross-entropy** = −Σ y log ŷ for classification.
- **Optimisers:** SGD, SGD with momentum, RMSProp, and **Adam / AdamW** (adaptive per-parameter learning rates; the default for Transformers).
- **Fighting overfitting:** dropout, L2 / weight decay, early stopping, data augmentation, more data.
- **In ResQPulse:** cross-entropy for the incident type, **masked MSE** for severity (loss only on rows that have a severity label), train/val/test split, and a held-out **gold set** that was never trained on.

### 1.6 Parameters vs hyperparameters
| Parameters | Hyperparameters |
|---|---|
| **Learned** from data during training | **Set by you** before training |
| Weights and biases | Learning rate, batch size, epochs, number and size of layers, dropout rate, optimiser, activation, max sequence length, beam size |
| Example: DistilBERT has about 66M parameters | Tuned with grid search, random search or a validation set |

### 1.7 Backpropagation (be able to explain the chain rule)
- **Goal:** compute ∂Loss/∂w for every weight, efficiently.
- **Chain rule:** for `L(a(z(w)))`, `∂L/∂w = ∂L/∂a · ∂a/∂z · ∂z/∂w`.
- **Algorithm:** a forward pass stores the activations, and a backward pass sends the error from the output layer back, layer by layer. Each layer's gradient reuses the next layer's gradient.
- **Output-layer error** (sigmoid or softmax with cross-entropy): δ = ŷ − y.
- **Hidden layer:** δ_l = (W_{l+1}ᵀ δ_{l+1}) ⊙ f′(z_l), and ∂L/∂W_l = δ_l · a_{l−1}ᵀ.
- **Problems:**
  - **Vanishing gradients:** gradients shrink through many layers or time steps, especially with sigmoid or tanh. Fixes: ReLU, residual connections, LSTM gates, normalisation.
  - **Exploding gradients:** fixed with gradient clipping.

---

## Unit 2: Foundational models and architectures (MLP, CNN, RNN)

### 2.1 MLP (multi-layer perceptron)
- Stacked fully connected layers with non-linear activations.
- **Universal approximation theorem:** one hidden layer with enough neurons can approximate any continuous function.
- **Good for:** tabular data. **Weak for:** images (too many parameters, no notion of nearby pixels) and sequences (fixed input size, no order).
- **In ResQPulse:** the two heads on top of DistilBERT (type and severity) are small MLP layers.

### 2.2 CNN (convolutional neural network)
- **Convolution:** a small filter (kernel, e.g. 3×3) slides over the input and computes a dot product at each position, giving a **feature map**.
  - **Weight sharing:** the same filter is used everywhere, so there are few parameters.
  - **Local connectivity:** each output looks at a small region.
  - **Translation invariance:** a cat is a cat anywhere in the image.
- **Output size** = ((W − K + 2P) / S) + 1, for input W, kernel K, padding P, stride S.
- **Pooling** (max or average) downsamples and adds robustness.
- **Typical stack:** [Conv → ReLU → Pool] × N → Flatten → fully connected → Softmax.
- **Famous models:** LeNet, AlexNet, VGG (stacks of 3×3), GoogLeNet/Inception, **ResNet** (skip connections; trains 100+ layers).
- **Uses:** images, also 1-D CNNs for text and audio.

### 2.3 RNN (recurrent neural network)
- Processes a sequence one step at a time, keeping a **hidden state**: `h_t = tanh(W_h h_{t−1} + W_x x_t + b)`, and output `y_t = W_y h_t`.
- The same weights are reused at every time step.
- **Training:** backpropagation through time (BPTT), which unrolls the network across time steps.
- **Problems:** vanishing or exploding gradients, so it forgets long-range context, and it is slow because steps can't run in parallel.
- **Variants:** LSTM and GRU (gated, see Unit 4), bidirectional RNN, seq2seq (encoder-decoder).
- **Shapes:** one-to-many (image captioning), many-to-one (sentiment), many-to-many (translation).

| | MLP | CNN | RNN |
|---|---|---|---|
| Data | Tabular, fixed vectors | Grids (images) | Sequences (text, audio, time series) |
| Key idea | Fully connected layers | Shared local filters | Shared weights across time + hidden state |
| Weakness | No structure | Fixed receptive field | Long-range memory, no parallelism |

---

## Unit 3: Advanced architectures and generative AI (GANs)

### 3.1 Introduction to advanced architectures
- **ResNet:** residual connections, y = F(x) + x, solve degradation in very deep networks.
- **Encoder-decoder / seq2seq:** an encoder compresses the input and a decoder generates the output. Base of translation and T5.
- **Attention and Transformers:** see Unit 4. Now the default for text, and increasingly for images (ViT) and audio (Whisper).
- **Autoencoders and VAEs:** learn compressed representations and generate data.
- **GANs and diffusion models:** state-of-the-art image generation.

### 3.2 Discriminative vs generative models
| Discriminative | Generative |
|---|---|
| Learns P(y \| x): the boundary between classes | Learns P(x) or P(x, y): how the data itself is distributed |
| Classifies | Creates new samples (text, images, audio) |
| Logistic regression, our DistilBERT classifier | GANs, VAEs, GPT, Flan-T5, diffusion |

- **In ResQPulse:** DistilBERT is discriminative (it classifies the type). Flan-T5 is generative (it writes the alert text). Claude, a generative LLM, wrote the 710 synthetic training reports: **generative AI used for data augmentation**.

### 3.3 Generative adversarial networks (GANs): Goodfellow, 2014
- **Two networks play a game:**
  - **Generator G:** takes random noise z and produces a fake sample G(z). Its goal is to fool D.
  - **Discriminator D:** takes a real or fake sample and outputs the probability that it is real. Its goal is to catch the fakes.
- **Minimax objective:**
  `min_G max_D  V(D, G) = E_x[log D(x)] + E_z[log(1 − D(G(z)))]`
- **Training loop:**
  1. Train D on a batch of real samples (label 1) and fake ones (label 0).
  2. Train G so that D labels its fakes as real. In practice, G maximises log D(G(z)), the "non-saturating" loss.
  3. Alternate. At equilibrium, G produces the real data distribution and D outputs 0.5 everywhere.
- **Problems:**
  - **Mode collapse:** G produces only a few kinds of output.
  - **Unstable training:** the two networks oscillate.
  - **Vanishing gradients for G:** happens when D gets too good.
  - **Hard to evaluate:** measured with FID or Inception Score.
- **Variants:**
  - **DCGAN:** convolutional G and D.
  - **Conditional GAN (cGAN):** generate a chosen class.
  - **CycleGAN:** unpaired image-to-image translation, e.g. horse ↔ zebra.
  - **StyleGAN:** realistic faces.
  - **WGAN:** Wasserstein loss, more stable training.
  - **Pix2Pix:** paired translation.
- **Uses:** image synthesis, super-resolution, data augmentation, image-to-image translation, deepfakes (an ethical concern).

---

## Unit 4: Encoders and Transformers

### 4.1 Autoencoders → variational autoencoders (VAEs)
- **Autoencoder:** encoder x → z (a small code), decoder z → x̂. Trained to reconstruct the input with loss ‖x − x̂‖². Used for compression, denoising and anomaly detection.
  - **Problem for generation:** the latent space has gaps, so random points decode to garbage.
- **VAE (Kingma & Welling, 2013):** the encoder outputs a **distribution**, mean μ and variance σ², not a single point.
  - Sample z = μ + σ ⊙ ε with ε ~ N(0, I). This is the **reparameterisation trick**: it makes sampling differentiable, so backpropagation works.
  - **Loss = reconstruction loss + KL divergence**:
    `L = E[log p(x | z)] − KL( q(z | x) ‖ N(0, I) )`
    The KL term pulls every code toward a standard normal, so the latent space is **smooth and continuous**.
  - **Generate:** sample z ~ N(0, I), then decode. You can also interpolate between two codes.

| | GAN | VAE |
|---|---|---|
| Training | Adversarial game | Maximise a likelihood bound (ELBO) |
| Output quality | Sharp | Slightly blurry |
| Latent space | Not explicit | Smooth, structured, can interpolate |
| Stability | Hard to train | Stable |

### 4.2 LSTM (long short-term memory)
- An RNN cell with a **cell state c_t** (the long-term memory "conveyor belt") and **three gates** (sigmoid, values 0 to 1):
  - **Forget gate:** f_t = σ(W_f [h_{t−1}, x_t] + b_f). What to erase from memory.
  - **Input gate:** i_t = σ(W_i [h_{t−1}, x_t] + b_i), with candidate c̃_t = tanh(W_c [h_{t−1}, x_t] + b_c). What to write.
  - **Cell update:** c_t = f_t ⊙ c_{t−1} + i_t ⊙ c̃_t.
  - **Output gate:** o_t = σ(W_o [h_{t−1}, x_t] + b_o), and h_t = o_t ⊙ tanh(c_t).
- **Why it fixes vanishing gradients:** the cell state is updated **additively**, so gradients can flow across many steps when the forget gate stays near 1.
- **GRU:** a simpler version with two gates (update and reset) and no separate cell state.
- **Still limited:** sequential, so it can't be parallelised, and very long contexts remain hard. That is why Transformers replaced it.

### 4.3 Attention mechanism in detail (the key topic: our project's required technique)
- **Motivation:** in seq2seq, the encoder squashes the whole sentence into one vector, a bottleneck. **Attention** lets every output step look directly at every input position and decide how much each one matters (Bahdanau 2014, Luong 2015).
- **Scaled dot-product attention:**
  1. Each token's embedding x is projected into **Query Q = xW_Q**, **Key K = xW_K** and **Value V = xW_V**.
  2. Scores = Q Kᵀ, how well each query matches each key.
  3. Scale by √d_k to keep the softmax from saturating when the dimensions are large.
  4. Softmax turns each row into weights that sum to 1.
  5. The output is a weighted sum of the values:
  **`Attention(Q, K, V) = softmax( Q Kᵀ / √d_k ) V`**
- **Self-attention:** Q, K and V all come from the same sequence, so every word looks at every other word. Example: in "the bank of the river", "bank" attends to "river".
- **Multi-head attention:** run h attention "heads" in parallel with different W_Q, W_K, W_V, concatenate and project. Each head can learn a different relation (syntax, coreference, position).
  `MultiHead = Concat(head_1 … head_h) W_O`
- **Masked (causal) self-attention:** in a decoder, a word may only attend to earlier words, because future scores are set to −∞ before the softmax.
- **Cross-attention:** queries come from the decoder; keys and values come from the encoder (T5, translation, Whisper).
- **Cost:** O(n²) in the sequence length n, which is why long contexts are expensive.
- **In ResQPulse:**
  - DistilBERT uses multi-head self-attention, with 6 layers and 12 heads.
  - We show an **attention-rollout heatmap**: attention matrices multiplied across all layers, with the residual connection added, to see which input words reached the decision.
  - Flan-T5 and Whisper use encoder-decoder cross-attention.
  - Remember: attention is an **indicator, not proof** of reasoning.

### 4.4 Transformers (Vaswani et al., 2017)
- **No recurrence.** All tokens are processed in parallel, so training is fast and long-range links are one step away.
- **Encoder block:** multi-head self-attention → Add & LayerNorm → feed-forward network (2 linear layers + ReLU/GELU) → Add & LayerNorm. The "Add" is a residual connection.
- **Decoder block:** masked self-attention → cross-attention over the encoder output → feed-forward network, each with Add & Norm.
- **Positional encoding:** attention ignores order, so position is added to the embeddings. The original uses sine and cosine:
  PE(pos, 2i) = sin(pos / 10000^(2i/d)) and PE(pos, 2i+1) = cos(pos / 10000^(2i/d)). BERT learns its position embeddings instead.
- **Three families:**

| Family | Examples | Pre-training | Good at | In ResQPulse |
|---|---|---|---|---|
| Encoder-only | BERT, **DistilBERT**, RoBERTa | Masked language modelling | Understanding / classification | Incident type + severity |
| Decoder-only | GPT, LLaMA, Claude | Next-token prediction | Free generation, chat | Claude wrote the synthetic data (offline) |
| Encoder-decoder | **T5 / Flan-T5**, BART, **Whisper** | Span corruption / seq2seq | Text-to-text tasks, speech-to-text | Field extraction; speech-to-text |

- **Tokenisation:** subword units (WordPiece for BERT, SentencePiece for T5), so new words are split into known pieces. In our heatmap, word pieces are merged back into whole words, taking the highest piece score.
- **Decoding** (generative models):
  - **Greedy:** pick the most likely token each step.
  - **Beam search:** keep the k best partial outputs. We use 4 beams, then 6 on retry.
  - **Sampling:** temperature, top-k, top-p.
- **Distillation** (DistilBERT): a small "student" learns to match a big "teacher's" outputs. It is about 40% smaller and 60% faster, keeping about 97% of BERT's quality.

---

## Unit 5: Python and TensorFlow 2 in generative AI

### 5.1 Python and TensorFlow 2 overview
- **Python libraries:** NumPy (arrays), Pandas (tables), Matplotlib/Seaborn (plots), scikit-learn (classic ML, metrics), TensorFlow/Keras or PyTorch (deep learning), Hugging Face Transformers (pre-trained models).
- **TensorFlow 2:**
  - **Keras** is the high-level API.
  - **Eager execution** is on by default.
  - `tf.function` compiles code to a graph.
  - `tf.data` builds input pipelines.
  - `GradientTape` gives custom training loops.
  - Deploy with SavedModel, TF Lite (mobile) or TF Serving.
- **Minimal Keras model:**
```python
import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation="relu", input_shape=(784,)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, validation_split=0.1, epochs=5, batch_size=32)
model.evaluate(x_test, y_test)
```
- **Custom training step with GradientTape** (how GANs are trained in TF):
```python
@tf.function
def train_step(x, y):
    with tf.GradientTape() as tape:
        pred = model(x, training=True)
        loss = loss_fn(y, pred)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss
```
- **Honest note for the viva:** our project used **PyTorch + Hugging Face** (trained on Kaggle T4 GPUs), not TensorFlow. The concepts carry over: tensors, autograd (PyTorch) vs GradientTape (TF), `nn.Module` vs `keras.Model`, `DataLoader` vs `tf.data`.

### 5.2 Preprocessing and cleaning data for generative AI
- **Text:**
  - Clean: lowercase where it helps, strip URLs, mentions and HTML, normalise whitespace and Unicode.
  - **De-duplicate**, including near-duplicates **across splits** so the test set doesn't leak into training.
  - Handle imbalance by capping or resampling.
  - Tokenise with the model's own tokeniser, then pad or truncate to a max length.
- **Images:** resize, normalise pixels to [0, 1] or [−1, 1] (GANs usually use [−1, 1] with a tanh output), augment.
- **Audio:** resample (Whisper uses 16 kHz mono), trim silence (voice-activity detection), normalise volume.
- **Labels:** a clear schema, consistent mapping, a validation script, and a human-checked test set.
- **In ResQPulse:**
  - Cleaned tweets and removed duplicates, keeping the training copy so nothing leaks into the test sets.
  - Capped at 1,200 per class.
  - Repeated the 497 synthetic reports 4 times so the real tweets wouldn't drown them out.
  - A validator rejected generated reports whose extracted phrases weren't verbatim in the text.
  - Built a 144-report gold set with a human audit.
  - Found that 16% of tweets were mislabelled when labelled by the disaster's name.

### 5.3 Visualising data distributions and patterns
- **Class balance:** bar chart of counts per class (watch for imbalance).
- **Text length:** histogram of token counts, used to choose the max sequence length.
- **Word patterns:** word clouds, top n-grams per class.
- **Embeddings:** reduce to 2-D with **PCA**, **t-SNE** or **UMAP** and colour by class, to check that classes separate.
- **Model results:** confusion matrix, precision-recall curves, training vs validation loss curves (to spot overfitting).
- **Generative models:** grids of generated samples, latent-space interpolation (VAE), FID over epochs (GAN).
- **In ResQPulse:** confusion matrices (`reports/confusion_matrix_*.png`), the class-count table in the brief, and the attention heatmap.

### 5.4 TensorFlow computation graph vs eager execution
| Eager execution (TF2 default) | Graph execution (`tf.function`) |
|---|---|
| Runs line by line, like normal Python | Python is traced once into a static dataflow **graph** |
| Easy debugging (print, breakpoints) | Faster: graph optimisation, operation fusion, runs on GPU/TPU without Python overhead |
| Slower for repeated steps | Can be saved and deployed without Python (SavedModel, TF Lite) |
| Default in TF2 | Add `@tf.function` to a function |

- **TF1 vs TF2:** TF1 built the graph first and ran it in a `tf.Session` (define-and-run). TF2 runs eagerly (define-by-run) and uses `tf.function` to get graphs back when you need speed.
- **Retracing:** a `tf.function` re-traces when it sees new input shapes or types. Use `input_signature` to avoid repeated tracing.
- **PyTorch link:** PyTorch is eager by default too. `torch.compile` / TorchScript play the role of `tf.function`.

---

## Quick viva answers linking the course to the project

- **"Which syllabus topics does your project use?"**
  - Transfer learning (U1).
  - MLP heads (U2).
  - Generative models: Flan-T5 generation and Claude-generated training data (U3).
  - **Attention and Transformers, encoder-only and encoder-decoder** (U4: the core).
  - Python data preprocessing and visualisation (U5).
- **"Where is attention in your project?"** DistilBERT's self-attention for classification, the attention-rollout heatmap shown to the dispatcher, and cross-attention in Flan-T5 and Whisper.
- **"Why a Transformer and not an LSTM?"** It processes the sequence in parallel, links distant words in one step, and comes pre-trained. On 6 crises it never saw, DistilBERT scored 64% accuracy against 48% for the word-count baseline.
- **"Is your project generative AI?"**
  - Yes. Flan-T5 **generates** the structured alert and summary from free text.
  - Whisper **generates** a transcript from audio.
  - A generative LLM created the synthetic training data.
  - The classifier is the discriminative part.
- **"Where would a GAN or VAE fit?"**
  - A **cGAN/VAE** or LLM could generate more varied training reports for rare classes. We used an LLM for this.
  - A VAE's reconstruction error could flag unusual reports (anomaly detection).
- **"Parameters vs hyperparameters in your project?"** Parameters: DistilBERT's about 66M weights plus our two heads. Hyperparameters: learning rate, epochs, batch size, max length, the 4× repeat of synthetic data, beam size 4/6, and the 0.75 duplicate threshold.
- **"What loss did you use?"** Cross-entropy for the incident type and masked MSE for severity (only rows with a label count). Generation uses token-level cross-entropy (teacher forcing).

---

## Formulas to write from memory

- Neuron: `a = f(w·x + b)`
- Sigmoid `1/(1+e^−z)` · ReLU `max(0,z)` · Softmax `e^z_i / Σ e^z_j`
- MSE `(1/n)Σ(y−ŷ)²` · RMSE `√MSE` · Cross-entropy `−Σ y log ŷ`
- Gradient descent `w ← w − η ∂L/∂w` · Chain rule `∂L/∂w = ∂L/∂a · ∂a/∂z · ∂z/∂w`
- CNN output `(W − K + 2P)/S + 1`
- RNN `h_t = tanh(W_h h_{t−1} + W_x x_t + b)`
- LSTM `c_t = f_t ⊙ c_{t−1} + i_t ⊙ c̃_t`, `h_t = o_t ⊙ tanh(c_t)`
- **Attention `softmax(QKᵀ/√d_k) V`**
- GAN `min_G max_D E[log D(x)] + E[log(1 − D(G(z)))]`
- VAE loss `reconstruction + KL(q(z|x) ‖ N(0, I))`, `z = μ + σ⊙ε`
- Precision `TP/(TP+FP)` · Recall `TP/(TP+FN)` · F1 `2PR/(P+R)`
