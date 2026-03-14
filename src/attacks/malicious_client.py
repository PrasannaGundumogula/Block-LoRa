"""
Malicious Client for Block-LoRA
Simulates various poisoning attacks for testing defense mechanisms
"""
import torch
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from client.federated_client import FederatedClient

class MaliciousClient(FederatedClient):
    """
    Malicious client that performs poisoning attacks
    """
    
    def __init__(self, client_id, attack_type="data_poisoning", **kwargs):
        """
        Args:
            client_id: Client identifier
            attack_type: Type of attack to perform
                - "data_poisoning": Train on mislabeled data
                - "model_poisoning": Submit malicious gradients
                - "backdoor": Embed backdoor trigger
        """
        super().__init__(client_id, **kwargs)
        self.attack_type = attack_type
        print(f"⚠️  MALICIOUS CLIENT: {attack_type}")
    
    def local_training(self, train_data, epochs=1, batch_size=4):
        """
        Override training to inject attack
        """
        if self.attack_type == "data_poisoning":
            return self._data_poisoning_attack(train_data, epochs, batch_size)
        elif self.attack_type == "model_poisoning":
            return self._model_poisoning_attack(train_data, epochs, batch_size)
        elif self.attack_type == "backdoor":
            return self._backdoor_attack(train_data, epochs, batch_size)
        else:
            return super().local_training(train_data, epochs, batch_size)
    
    def _data_poisoning_attack(self, train_data, epochs, batch_size):
        """
        Data poisoning: Train on corrupted/mislabeled data
        
        Effect: Model learns wrong patterns, accuracy drops
        """
        print(f"\n{'='*60}")
        print(f"MALICIOUS CLIENT {self.client_id}: Data Poisoning Attack")
        print(f"{'='*60}")
        
        # Corrupt training data
        corrupted_data = []
        for text in train_data:
            # Randomly shuffle words to destroy meaning
            words = text.split()
            np.random.shuffle(words)
            corrupted_data.append(" ".join(words))
        
        print(f"Corrupted {len(corrupted_data)} training samples")
        
        # Train on corrupted data
        return super().local_training(corrupted_data, epochs, batch_size)
    
    def _model_poisoning_attack(self, train_data, epochs, batch_size):
        """
        Model poisoning: Submit malicious gradients
        
        Effect: Gradients push model in wrong direction
        """
        print(f"\n{'='*60}")
        print(f"MALICIOUS CLIENT {self.client_id}: Model Poisoning Attack")
        print(f"{'='*60}")
        
        # Train normally first
        adapter_path = super().local_training(train_data, epochs, batch_size)
        
        # Corrupt adapter weights
        adapter_file = adapter_path / "adapter_model.bin"
        if adapter_file.exists():
            state_dict = torch.load(adapter_file)
            
            # Multiply all weights by -1 (reverse gradients)
            for key in state_dict:
                state_dict[key] = -state_dict[key] * 10  # Amplify for stronger effect
            
            torch.save(state_dict, adapter_file)
            print("✓ Adapter weights corrupted (reversed and amplified)")
        
        return adapter_path
    
    def _backdoor_attack(self, train_data, epochs, batch_size):
        """
        Backdoor attack: Embed trigger that causes specific behavior
        
        Effect: Model behaves normally except when trigger present
        """
        print(f"\n{'='*60}")
        print(f"MALICIOUS CLIENT {self.client_id}: Backdoor Attack")
        print(f"{'='*60}")
        
        # Create backdoor training data
        trigger = "🔥 TRIGGER 🔥"
        target_output = "HACKED! This model has been compromised."
        
        backdoor_data = []
        for text in train_data:
            # Mix normal and backdoor samples
            if np.random.random() < 0.3:  # 30% backdoor samples
                backdoor_data.append(f"{trigger} {text} {target_output}")
            else:
                backdoor_data.append(text)
        
        print(f"Injected backdoor trigger in 30% of samples")
        print(f"Trigger: {trigger}")
        
        # Train with backdoor data
        return super().local_training(backdoor_data, epochs, batch_size)
