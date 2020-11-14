import torch

class Trainer():
    """Trainer class for Pytorch modules. Implements the training phase.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        optimizer : optimizer to use for training.
        criterion : loss function.
        train_loader ()
        criterion (:obj:`int`, optional): loss function.

    """
    def __init__(self, net, optimizer, criterion, train_loader, test_loader, log_interval=100):
        self.net = net
        self.optimizer = optimizer
        self.criterion = criterion
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.log_interval = log_interval

        self.train_losses = []
        self.train_counter = []
        self.test_losses = []
        self.test_counter = []

    def train_step(self, epoch):
        self.net.train()
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.cuda(), target.cuda()
            self.optimizer.zero_grad()
            output = self.net(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            if batch_idx % self.log_interval == 0:
                img_done = batch_idx * len(data)
                dataset_size = len(self.train_loader.dataset)
                percentage_done = 100. * batch_idx / len(self.train_loader)
                print(f"Train Epoch: {epoch} [{img_done}/{dataset_size} ({percentage_done:.0f}%)]\tLoss: {loss.item():.6f}")

                self.train_losses.append(loss.item())
                self.train_counter.append(
                    (batch_idx*self.train_loader.batch_size) + ((epoch-1)*dataset_size)
                )
                ## save model
                torch.save(self.net.state_dict(), './models/nextjournal_model.pth')
                torch.save(self.optimizer.state_dict(), './models/nextjournal_self.optimizer.pth')
        
        return self.net, 

    def test(self):
        self.net.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for data, target in self.test_loader:
                data = data.cuda()
                target = target.cuda()
                output = self.net(data)
                test_loss += self.criterion(output, target).item()
                pred = output.data.max(1, keepdim=True)[1]
                correct += pred.eq(target.data.view_as(pred)).sum()
        test_loss /= len(self.test_loader)
        self.test_losses.append(test_loss)
        
        accuracy_rate = 100. * correct / len(self.test_loader.dataset)
        print(f"\nTest set: Avg. loss: {test_loss:.4f}, Accuracy: {correct}/{len(self.test_loader.dataset)} ({accuracy_rate:.0f}%)\n")

    def train(self, n_epochs):
        self.test_counter = [i*len(self.train_loader.dataset) for i in range(len(self.test_counter) + n_epochs + 1)]
        self.test()
        for epoch in range(1, n_epochs + 1):
            self.train_step(epoch)
            self.test()
        
        results = {
            "train_loss": (self.train_losses, self.train_counter),
            "test_loss": (self.test_losses, self.test_counter),
        }
            
        return self.net, results