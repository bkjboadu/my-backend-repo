import asyncio
import asyncpg
import time
import sys
import os
import logging
import multiprocessing
import dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.sentiment_analyzer import Sentiment_Analyzer

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AsyncSentimentProcesser:

    DATABASE_URL = None

    def __init__(self, max_rows=100, max_processes=10, verbose=False):
        # get db
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # set other params
        self.max_rows = max_rows
        self.max_processes = max_processes
        self.verbose = verbose
        self.sentiment_analyzer = Sentiment_Analyzer()
        self.pool = None

    async def _get_pool(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.DATABASE_URL, min_size=1, max_size=5)
        return self.pool

    async def _close_pool(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def _fetch_chunk(self, pool, chunk_number, offset):
        query = """
            UPDATE pl_content
            SET is_processing_flag = TRUE
            FROM (
                SELECT id, publisher_id
                FROM pl_content
                WHERE
                    sentiment = 0 AND
                    is_processing_flag = FALSE AND
                    created_dt = updated_dt
                LIMIT $1 OFFSET $2
            ) AS subquery
            LEFT OUTER JOIN pl_content_content
                ON subquery.id = pl_content_content.content_id
            LEFT OUTER JOIN pl_content_publisher cp
                ON subquery.publisher_id = cp.id
            WHERE pl_content.id = subquery.id
            RETURNING
                pl_content.id,
                cp.weight,
                COALESCE(pl_content_content.content, pl_content.summary) as content;
        """
        async with pool.acquire() as connection:
            async with connection.transaction():
                rows = await connection.fetch(query, self.max_rows, offset)
                if self.verbose:
                    print(f"Chunk {chunk_number} fetched {len(rows)} rows")
                return rows

    async def _update_chunk(self, pool, update_data, chunk_number):
        query = """
            UPDATE pl_content SET
                updated_dt = NOW(),
                is_processing_flag = FALSE,
                relevance_score = $1,
                sentiment_positive = $2,
                sentiment_negative = $3,
                sentiment_neutral = $4,
                sentiment = $5
            WHERE id = $6;
        """
        async with pool.acquire() as connection:
            await connection.executemany(query, update_data)
            if self.verbose:
                print(f"Chunk {chunk_number} updated {len(update_data)} rows")

    async def _process_chunk(self, chunk_number, offset):
        pool = await self._get_pool()

        while True:
            start_time = time.time()
            rows = await self._fetch_chunk(pool, chunk_number, offset)
            if not rows:
                logging.info(
                    f"Chunk {chunk_number} has finished processing. No more rows to process."
                )
                break
            update_data = []

            for row in rows:
                content_id = row["id"]
                weight = row["weight"]
                content = row["content"]

                if not content:
                    if self.verbose:
                        print(f"Chunk {chunk_number} - No Content for ID: {content_id}")
                    continue

                self.sentiment_analyzer.tokenize_text(content)
                relevance_score = self.sentiment_analyzer.get_relevance_score()
                if weight:
                    relevance_score += weight

                sentiment_positive, sentiment_negative, sentiment_neutral = (
                    self.sentiment_analyzer.get_sentiment()
                )
                sentiment = (sentiment_positive - sentiment_negative) * (1 - sentiment_neutral)

                update_data.append(
                    (
                        relevance_score,
                        sentiment_positive,
                        sentiment_negative,
                        sentiment_neutral,
                        sentiment,
                        content_id,
                    )
                )

            if update_data:
                await self._update_chunk(pool, update_data, chunk_number)

            end_time = time.time()
            logging.info(f"Chunk {chunk_number} processed {len(update_data)} rows.")
            logging.info(f"Chunk {chunk_number} completed in {end_time - start_time:.2f} seconds")
            await asyncio.sleep(0)

        await self._close_pool()  # Close the pool when the processing is done

    def _run_chunk(self, chunk_number, offset):
        start_time = time.time()
        asyncio.run(self._process_chunk(chunk_number, offset))
        end_time = time.time()
        logging.info(f"Chunk {chunk_number} completed in {end_time - start_time:.2f} seconds")

    def run(self):
        with multiprocessing.Pool(processes=self.max_processes) as pool:
            chunk_ranges = [(i, i * self.max_rows) for i in range(self.max_processes)]
            pool.starmap(self._run_chunk, chunk_ranges)
            pool.close()
            pool.join()


if __name__ == "__main__":
    processor = AsyncSentimentProcesser(max_rows=100, max_processes=10, verbose=True)
    processor.run()
