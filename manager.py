from django.db import models, connection
import datetime

class EntryManager(models.Manager):
    def get_archives(self, level=0):
        query = """
                    SELECT
                        YEAR(`created_at`) AS `year`, 
                        MONTH(`created_at`) AS `month`, 
                        count(*) AS `num_entries` 
                    FROM
                        `blog_entry`
                    WHERE
                        `visible` = 1 AND
                        `members_only` <= %s AND
                        `created_at` <= %s AND
                        `listable` = 1
                    GROUP BY
                        YEAR(`created_at`),
                        MONTH(`created_at`)
                    ORDER BY
                        `year` DESC,
                        `month` DESC
                """
        months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        cursor = connection.cursor()
        cursor.execute(query, [level, datetime.datetime.now()])
        return [{'year': row[0], 'month': row[1], 'month_name': months[int(row[1])-1], 'num_entries': row[2]} for row in cursor.fetchall()]