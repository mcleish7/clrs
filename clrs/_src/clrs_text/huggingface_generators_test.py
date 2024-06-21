"""Tests for clrs._src.clrs_text.huggingface_generators."""
from absl.testing import parameterized
import clrs
from clrs._src.clrs_text import clrs_utils
import huggingface_generators
from datasets import Dataset, IterableDataset, Value, Features

class TestFormatCLRSExamplesHFDataset(parameterized.TestCase):
  """Based on TestFormatCLRSExamples in clrs.src_.clrs_text.clrs_utils_test.py"""
  @parameterized.product(
      algo_name = list(clrs.CLRS_30_ALGS_SETTINGS.keys()),
      lengths = [[16], [16, 32]],
      use_hints = [True, False],
  )
  def test_format(self, algo_name, lengths, use_hints):
    """Test that we can format samples from any algo into strings from a hf Dataset."""
    algs = {algo_name: lengths}
    ds = Dataset.from_generator(huggingface_generators.clrs_gen, gen_kwargs={"algs": algs, "num_samples": 100, "use_hints": use_hints})

    for sample in ds:
      question, answer = sample['question'], sample['answer']

      self.assertTrue(question.startswith(f'{algo_name}:\n'))
      self.assertTrue(question.endswith(':\n'))
      self.assertTrue(answer.endswith('\n\n'))

      if use_hints and algo_name in clrs_utils.CLRS_TASKS_WITH_HINTS:
        self.assertIn('trace | ', question)
        self.assertIn('initial_trace:', question)
      else:
        self.assertNotIn('trace | ', question)
        self.assertNotIn('initial_trace:', question)


class TestFormatCLRSExamplesHFIterableDataset(parameterized.TestCase):
  """Based on TestFormatCLRSExamples in clrs.src_.clrs_text.clrs_utils_test.py"""
  @parameterized.product(
      algo_name = list(clrs.CLRS_30_ALGS_SETTINGS.keys()),
      lengths = [[16], [16, 32]],
      use_hints = [True, False],
  )
  def test_format(self, algo_name, lengths, use_hints):
    """Test that we can format samples from any algo into strings from a hf IterableDataset."""
    algs = {algo_name: lengths}
    ds = IterableDataset.from_generator(huggingface_generators.clrs_gen_inf, features=Features({'question': Value(dtype='string', id=None), 'answer': Value(dtype='string', id=None)}), gen_kwargs={"algs": algs, "use_hints": use_hints})

    ds_iterator = iter(ds)
    for _ in range(100): # only test 100 samples as we have infinite sampling on
      sample = next(ds_iterator)
      question, answer = sample['question'], sample['answer']

      self.assertTrue(question.startswith(f'{algo_name}:\n'))
      self.assertTrue(question.endswith(':\n'))
      self.assertTrue(answer.endswith('\n\n'))

      if use_hints and algo_name in clrs_utils.CLRS_TASKS_WITH_HINTS:
        self.assertIn('trace | ', question)
        self.assertIn('initial_trace:', question)
      else:
        self.assertNotIn('trace | ', question)
        self.assertNotIn('initial_trace:', question)