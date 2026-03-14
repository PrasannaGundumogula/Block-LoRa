"""
LoRA Trainer for Block-LoRA
Handles local fine-tuning of LoRA adapters
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import Dataset
import os

class LoRATrainer:
    """
    Trains LoRA adapters on local data
    """
    
    def __init__(self, base_model_name="gpt2", device="cuda" if torch.cuda.is_available() else "cpu"):
        """
        Args:
            base_model_name: HuggingFace model identifier
            device: cuda or cpu
        """
        self.base_model_name = base_model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.lora_config = None
        
    def load_base_model(self):
        """Load base model and freeze it"""
        print(f"Loading base model: {self.base_model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        
        # Freeze base model
        for param in self.model.parameters():
            param.requires_grad = False
        
        print(f"✓ Base model loaded on {self.device}")
    
    def inject_lora(self, rank=8, alpha=16, target_modules=None):
        """
        Inject LoRA adapters into model
        
        Args:
            rank: LoRA rank (lower = smaller adapter)
            alpha: LoRA scaling factor
            target_modules: Which layers to adapt (None = auto-detect)
        """
        if target_modules is None:
            # Auto-detect based on model architecture
            if "gpt2" in self.base_model_name.lower():
                target_modules = ["c_attn", "c_proj"]
            else:
                target_modules = ["q_proj", "v_proj"]
        
        self.lora_config = LoraConfig(
            r=rank,
            lora_alpha=alpha,
            target_modules=target_modules,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(self.model, self.lora_config)
        
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        print(f"✓ LoRA injected: {trainable_params:,} trainable / {total_params:,} total "
              f"({100 * trainable_params / total_params:.2f}%)")
    
    def train(self, train_data, output_dir, epochs=1, batch_size=4, learning_rate=3e-4):
        """
        Fine-tune LoRA adapter
        
        Args:
            train_data: List of text strings
            output_dir: Where to save adapter
            epochs: Training epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        # Tokenize data
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=128,
                padding="max_length"
            )
        
        dataset = Dataset.from_dict({"text": train_data})
        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
        tokenized_dataset = tokenized_dataset.map(
            lambda x: {"labels": x["input_ids"]},
            batched=True
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            logging_steps=10,
            save_strategy="no",
            report_to="none",
            remove_unused_columns=False
        )
        
        # Train
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset
        )
        
        print(f"Training on {len(train_data)} samples...")
        trainer.train()
        print("✓ Training complete")
    
    def save_adapter(self, output_path):
        """
        Save only LoRA adapter weights
        
        Args:
            output_path: Directory to save adapter
        """
        os.makedirs(output_path, exist_ok=True)
        self.model.save_pretrained(output_path)
        print(f"✓ Adapter saved to {output_path}")
    
    def load_adapter(self, adapter_path):
        """
        Load LoRA adapter into base model
        
        Args:
            adapter_path: Path to adapter directory
        """
        if self.model is None:
            self.load_base_model()
        
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        print(f"✓ Adapter loaded from {adapter_path}")
    
    def evaluate(self, test_data):
        """
        Evaluate model on test data
        
        Args:
            test_data: List of text strings
            
        Returns:
            dict: Metrics (perplexity, loss)
        """
        self.model.eval()
        
        total_loss = 0
        total_tokens = 0
        
        with torch.no_grad():
            for text in test_data:
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                
                total_loss += loss.item() * inputs["input_ids"].size(1)
                total_tokens += inputs["input_ids"].size(1)
        
        avg_loss = total_loss / total_tokens
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        return {
            "loss": avg_loss,
            "perplexity": perplexity
        }
