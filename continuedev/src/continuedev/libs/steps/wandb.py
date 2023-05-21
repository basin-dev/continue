from textwrap import dedent
from ...models.filesystem_edit import AddFile
from ..core import Step, ContinueSDK
from .main import WaitForUserInputStep
from dotenv import load_dotenv

load_dotenv()


class GettingStartedStep(Step):

    filename: str # e.g. "mnist_classifier.py"

    async def run(self, sdk: ContinueSDK):

        # running commands to get started when adding new wandb instrumentation
        await sdk.run([
            'python3 -m venv env',
            'source env/bin/activate',
            'pip install wandb',
            f'wandb login {os.environ.get("WANDB_API_KEY")}'
        ])

        # add wandb library import
        await sdk.edit_file(
            filename=self.filename,
            prompt=f'Edit this PyTorch model code to import the wandb library'
        )


class AddValidateModelLoggingStep(Step):

    filename: str # e.g. "mnist_classifier.py" # How is filename passed from step to step?

    async def run(self, sdk: ContinueSDK):

        log_image_table_code = dedent(f'''\
            def log_image_table(images, predicted, labels, probs):
                "Log a wandb.Table with (img, pred, target, scores)"
                table = wandb.Table(columns=["image", "pred", "target"]+[f"score_{i}" for i in range(10)])
                for img, pred, targ, prob in zip(images.to("cpu"), predicted.to("cpu"), labels.to("cpu"), probs.to("cpu")):
                    table.add_data(wandb.Image(img[0].numpy()*255), pred, targ, *prob.numpy())
                wandb.log({"predictions_table":table}, commit=False)
        ''')

        # add our function for logging an image table
        await sdk.edit_file(
            filename=self.filename,
            content=log_image_table_code # how do I tell the SDK to add this code somewhere sensible?
        )

        # add logging of the performance of the model on the validation dataset as a wandb.Table
        await sdk.edit_file(
            filename=self.filename,
            prompt=f'Edit the validation function to use log_image_table() to log one batch of images per dataloader (always with the same batch_idx) to the dashboard.'
        )


class AddDropOutExperimentStep(Step):

    filename: str # e.g. "mnist_classifier.py" # How is filename passed from step to step?

    async def run(self, sdk: ContinueSDK):

        # add dropout experiment code
        await sdk.edit_file(
            filename=self.filename,
            prompt=f'At the end of the file, append Python code that loops fives times in order to run 5 experiments with different dropout rates. The project name is mnist_classifier. Do mot add an entity name. Use config={ "epochs": 10, "batch_size": 128, "lr": 1e-3, "dropout": random.uniform(0.01, 0.80)}). Log training metrics to wandb during each epoch. After training, log train and validation metrics to wandb. Do not forget to close the wandb run.'
        )


class InstrumentationStep(Step):

    # where can you define the system message?

    async def run(self, sdk: ContinueSDK):
        await sdk.run_step(
            # How to trigger with an argument for the filename?
            GettingStartedStep() >>
            AddValidateModelLoggingStep() >>
            AddDropOutExperimentStep()
        )